import os
from datetime import datetime
import csv
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class BirthdayEmail:
    # Constructor method to initialize a new BirthdayEmail object.
    # It sets up a MIME multipart email message container.    
    def __init__(self) -> None:
        self.message = MIMEMultipart()

    # Set up a new email message with sender, recipient, and subject.
    # Raises exceptions for invalid inputs (empty strings).
    def new_message(self, from_email, recipient_email):
        if from_email == "":
            raise Exception("Invalid (empty) recipient")
        if recipient_email == "":
            raise Exception("Invalid (empty) recipient")
        self.message['From'] = from_email
        self.message['To'] = recipient_email
        self.message['Subject'] = "Happy Birthday!"


    # Add an email body to the message.
    # It attaches a MIMEText part with the email body in plain text format.
    # Raises an exception if the body text is empty.
    def add_body(self, body):
        if len(body) < 1:
            raise Exception("Invalid (empty) email body supplied")
        self.message.attach(MIMEText(body, 'plain'))

    # Prepare the email for sending.
    # It returns the sender and recipient email addresses, and the email message as a string.
    def prepare(self):
        from_email = self.message['From']
        to_email = self.message['To']
        text = self.message.as_string()
        return from_email, to_email, text



class SMTPServer:
    # Constructor for initializing an SMTPServer object with server type, user credentials.
    # It sets up the SMTP server and port based on the specified type.
    # Raises an exception for unsupported server types.
    def __init__(self, type, user, password) -> None:
        self._user = user
        self._password = password
        if type == "Outlook": # Add more options here
            self._smtp_server = "smtp-mail.outlook.com"
            self._smtp_port = 587
        else:
            raise Exception("Invalid SMTP server type")

    # Send an email using the SMTP server.
    # It requires the sender's email, recipient's email, and the email text (including headers).        
    def send(self, from_email, to_email, text):
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
            server.starttls() # Upgrade the connection to secure
            print("connected to server")
            server.login(self._user, self._password)
            print("logged in as user {}".format(self._user))
            server.sendmail(from_email, to_email, text)
            print("email sent")

def read_account():
    sender_name = os.getenv("MY_NAME")
    if not sender_name:
        raise Exception("os env MY_NAME is empty")
    email = os.getenv("MY_EMAIL")
    if not email:
        raise Exception("os env MY_EMAIL is empty")
    password = os.getenv("MY_EMAIL_PSWD")
    if not password:
        raise Exception("os env MY_EMAIL_PSWD is empty")
    return sender_name, email, password

def filter_birthdays(csv_filename, today): # TODO - improve by eliminating need to return non-essential rows
    # Get the current day and month
    current_month = today.month
    current_day = today.day

    matching_entries = []
    remaining_entries = []

    # Open and read the CSV file
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert month and day from the CSV to integers
            month = int(row['month'])
            day = int(row['day'])

            completed = int(row['completed'])
            if completed != 0:
                email = row['email']
                print("Email to {} already sent".format(email))
                continue
            
            # Check if the entry matches today's date
            if month == current_month and day == current_day:
                matching_entries.append(row)
            else:
                remaining_entries.append(row)

    return matching_entries, remaining_entries

def set_completed(csv_filename, updated_rows, rest):
    # Write the updated data back to the CSV
    with open("temp.csv", mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['name', 'email', 'month', 'day', 'completed'] 
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
        writer.writerows(rest) # TODO - improve
    # Replace the original file with the updated data
    os.replace("temp.csv", csv_filename)

def send_birthday_emails(csv_filename, template_filename):
    """
    * Read birthdays from CSV file.
    * Read template from txt files.
    * Read ENV variables to get user name and email account details.
    * Send Birthday emails.
    * Update CSV emails.
    """
    today = datetime.now()
    print("----------", today,"----------")

    birthdays_today, rest = filter_birthdays(csv_filename, today)
    if len(birthdays_today) < 1:
        print("No birthday messages to send!")
        quit()

    sender_name, from_email, password = read_account()

    # Start server
    server = SMTPServer("Outlook", from_email, password)

    updated_rows = []

    for entry in birthdays_today:
        name = entry['name']
        recipient_email = entry['email']

        mail = BirthdayEmail()
        mail.new_message(from_email, recipient_email)

        # Create personalized email 
        # Read from template birthday message
        with open(template_filename, 'r', encoding='utf-8') as file:
            msg = file.read()
            msg = msg.replace("[NAME]", name)
            msg = msg.replace("[SENDER]", sender_name)

        print("Preparing email from {} ({}) to {}".format(from_email, sender_name, recipient_email))

        # Prepare text body
        mail.add_body(msg)
        # Send email
        fr, to, text = mail.prepare()
        server.send(fr, to, text)

        # Set to completed in CSV
        entry['completed'] = '1'
        updated_rows.append(entry)

    set_completed(csv_filename, updated_rows, rest)

if __name__=="__main__":
    # Pick later template at random
    template_filepath = f"templates/letter{random.randint(1,2)}.txt"
    # Send email
    send_birthday_emails("birthdays.csv", template_filepath)