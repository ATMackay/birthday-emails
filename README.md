# Auto Birthday Email Generator in Python

## Getting started

Set environment variables
```
$ export MY_NAME=<your_name>
$ export MY_EMAIL=<your_email>
$ export MY_EMAIL_PSSWD=<your_email_password>
```

Add a customized `birthdays.csv`
```
$ cp birthdays.csv.tpl birthdays.csv
```

Add contact and birthday information to the file.

Run
```
$ python3 birthday_emails.py 
Preparing email from <your_email> (<your_name>) to <recipient_email>
connected to server
logged in as user <your_email>
email sent
```

## Creating a birthday message cronjob (Linux)

* In the terminal, run `crontab -e` to edit the cron table. This will open your crontab file in the default text editor. If you're asked to select an editor and are unsure, choose `nano` (it's user-friendly).
* In the crontab file, add a line specifying when the cron job should run and the command to execute your Python script. The general format is:
```
* * * * * command to execute
```
In our case
```
MY_NAME=<your_name>
MY_EMAIL=<your_email>
MY_EMAIL_PSSWD=<your_email_password>
0 * * * * cd /path/to/file/ && /usr/bin/python3 /path/to/file/birthday_emails.py
```
Will run the python script every hour indefinitely. Or if you want to save the output
```
0 * * * * cd /path/to/file/ && /usr/bin/python3 birthday_emails.py >> /home/<username>/birthday_emails_log.txt 2>&1
```

Alternatively, to avoid storing sensitive data in your crontab create `env_vars.sh` file with 
```
MY_NAME=<your_name>
MY_EMAIL=<your_email>
MY_EMAIL_PSSWD=<your_email_password>
```

```
chmod +x /path/to/env_vars.sh
chmod 600 /path/to/env_vars.sh
```

Update your cronjob
```
0 * * * * . /path/to/env_vars.sh; cd /path/to/file/ && /usr/bin/python3 /path/to/file/birthday_emails.py
```