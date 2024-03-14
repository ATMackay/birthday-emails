import os
from datetime import datetime
import csv
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class BirthdayEmail:
    """
    A class to create and manage birthday emails.
    """
    def __init__(self):
        """
        Initializes a new BirthdayEmail object with an empty email message.
        """
        self.message = MIMEMultipart()

    def new_message(self, from_email, recipient_email):
        """
        Sets up a new email message with sender, recipient, and a fixed subject.
        """
        if not from_email:
            raise ValueError("Invalid (empty) sender")
        if not recipient_email:
            raise ValueError("Invalid (empty) recipient")
        self.message['From'] = from_email
        self.message['To'] = recipient_email
        self.message['Subject'] = "Happy Birthday!"

    def add_body(self, body):
        """
        Adds an email body to the message.
        """
        if not body:
            raise ValueError("Invalid (empty) email body supplied")
        self.message.attach(MIMEText(body, 'plain'))

    def prepare(self):
        """
        Prepares the email for sending.
        """
        from_email = self.message['From']
        to_email = self.message['To']
        text = self.message.as_string()
        return from_email, to_email, text



class SMTPServer:
    """
    A class to manage SMTP server connection and send emails.
    """
    def __init__(self, server_type, user, password):
        """
        Initializes an SMTPServer object with server details.
        """
        self.user = user
        self.password = password
        if server_type == "Outlook":
            self.smtp_server = "smtp-mail.outlook.com"
            self.smtp_port = 587
        else:
            raise ValueError("Invalid SMTP server type")
        # Initialize the host attribute to None. It will be set in the connect method.
        self.host = None

    def connect(self):
        """
        Connects to the SMTP server using the credentials provided during initialization.
        """
        try:
            self.host = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self.host.starttls()
            print("Connected to server")
            self.host.login(self.user, self.password)
            print(f"Logged in as user {self.user}")
        except smtplib.SMTPException as e:
            raise SystemError(e) from e

    def send(self, from_email, to_email, text):
        """
        Sends the supplied email via the connected SMTP server.
        """
        if not self.host:
            raise SystemError("SMTP connection not established. Please run connect() first.")
        try:
            self.host.sendmail(from_email, to_email, text)
        except smtplib.SMTPException as e:
            raise e

    def close(self):
        """
        Closes the connection to the SMTP server.
        """
        if self.host:
            self.host.quit()
            self.host = None
            print("Disconnected from server")

def read_account():
    """
    Reads account details from environment variables.
    """
    sender_name = os.getenv("MY_NAME")
    if not sender_name:
        raise EnvironmentError("Environment variable MY_NAME is empty")
    email = os.getenv("MY_EMAIL")
    if not email:
        raise EnvironmentError("Environment variable MY_EMAIL is empty")
    password = os.getenv("MY_EMAIL_PSWD")
    if not password:
        raise EnvironmentError("Environment variable MY_EMAIL_PSWD is empty")
    return sender_name, email, password

def filter_birthdays(csv_filename, today):
    """
    Filters entries in a CSV file to find and separate birthdays matching today's date.
    It also separates entries already marked as completed to avoid re-sending emails.
    
    Args:
        csv_filename (str): The path to the CSV file containing birthday information.
        today (datetime): The current date.
    
    Returns:
        tuple: Two lists of dictionaries, the first with matching entries for today, 
               and the second with the rest of the entries.
    """
    current_month = today.month
    current_day = today.day

    matching_entries = []
    remaining_entries = []

    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:

            month, day, completed = int(row['month']), int(row['day']), int(row['completed'])           
            if completed != 0:
                continue  # Skip already completed entries
            if month == current_month and day == current_day:
                matching_entries.append(row)
            else:
                remaining_entries.append(row)

    return matching_entries, remaining_entries

def set_completed(csv_filename, updated_rows):
    """
    Updates the CSV file to mark selected entries as completed.

    Args:
        csv_filename (str): The path to the CSV file.
        updated_rows (list): A list of dictionaries representing the rows to update.
    """
    temp_filename = f"{csv_filename}.tmp"

    with open(temp_filename, mode='w', encoding='utf-8', newline='') as file:
        fieldnames = ['name', 'email', 'month', 'day', 'completed']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    os.replace(temp_filename, csv_filename)

def send_birthday_emails(csv_filename, template_filename):
    """
    Main function to orchestrate reading birthdays, sending emails, and updating the CSV.
    """
    today = datetime.now()
    print(f"---------- {today} ----------")

    birthdays_today, _ = filter_birthdays(csv_filename, today)
    if not birthdays_today:
        print("No birthday messages to send!")
        return

    sender_name, from_email, password = read_account()
    server = SMTPServer("Outlook", from_email, password)
    server.connect()
    

    updated_rows = []
    try:
        for entry in birthdays_today:
            with open(template_filename, 'r', encoding='utf-8') as file:
                msg = file.read().replace("[NAME]", entry['name']).replace("[SENDER]", sender_name)

            # Create email body
            mail = BirthdayEmail()
            mail.new_message(from_email, entry['email'])
            mail.add_body(msg)
            fr, to, text = mail.prepare()

            # Attempt send
            try:
                server.send(fr, to, text)
                entry['completed'] = '1'
                updated_rows.append(entry)
                print(f"Email sent to {entry['email']}")
            except Exception as e:
                print(f"Failed to send email to {entry['email']}: {e}")

        if updated_rows:
            set_completed(csv_filename, updated_rows + _)
    finally:
        server.close()

def main():
    """
    Main execution function: selects a random template and sends personalized birthday emails
    to recipients in 'birthdays.csv' on the correct day.
    """
    # Path to the directory containing email templates
    template_directory = "templates"
    # Randomly select a template
    template_filename = f"{template_directory}/letter{random.randint(1, 2)}.txt"
    # CSV file containing the birthdays
    csv_filename = "birthdays.csv"    
    # Execute the primary function to process birthdays and send emails
    send_birthday_emails(csv_filename, template_filename)

if __name__ == "__main__":
    main()