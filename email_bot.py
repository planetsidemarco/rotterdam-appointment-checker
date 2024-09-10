"""
06/08/24
Marco Tyler-Rodrigue
Selenium webscraper for checking rotterdam municipality appointment times
"""

import os
from typing import List
from datetime import datetime
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from dotenv import load_dotenv


def current_datetime() -> str:
    """Helper function to return datetime string

    Returns:
        str: YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class EmailBot:
    """Email bot class"""

    def __init__(self):
        # Load environment secrets
        env_path = Path("./emailpass.env")
        load_dotenv(dotenv_path=env_path)

        # Set parameters from environment secrets
        self.bot_email = f"{os.environ.get('EMAIL_SENDER')}@gmail.com"
        self.bot_pass = os.environ.get("EMAIL_APP_PASS")
        self.receiver_email = f"{os.environ.get('EMAIL_RECEIVER')}@gmail.com"

        self.file_contents = ""
        self.attachments = []

        self.message = MIMEMultipart()

    def read_file_contents(self, file_name: str):
        """Helper function to read file contents

        Args:
            file_name (str): name of file to read
        """
        with open(file_name, "r", encoding="utf-8") as file:
            self.file_contents = file.read()

    def check_for_attachements(self, allowed_attachments: List):
        """Helper function to check if attachments are required

        Args:
            allowed_attachments (List): list of allowed attachments
        """
        filtered_files = [
            file
            for file in os.listdir(".")
            if (os.path.isfile(file) and file.lower().endswith((".png")))
        ]
        for filename in filtered_files:
            if filename in allowed_attachments:
                self.attachments.append(filename)

    def create_message(self, subject: str):
        """Function to create email message

        Args:
            subject (str): subject of email message
        """
        self.message["From"] = self.bot_email
        self.message["To"] = self.receiver_email
        self.message["Subject"] = subject

    def add_message_body(self, body: str):
        """Function to add body to email message

        Args:
            body (str): body of email message
        """
        self.message.attach(MIMEText(body, "plain"))

    def add_attachments(self):
        """Function to add attachments to email message"""
        for attachment in self.attachments:
            filename = os.path.basename(attachment)
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                with open(attachment, "rb") as f:
                    img = MIMEImage(f.read(), name=filename)
                    self.message.attach(img)
            else:
                with open(attachment, "rb") as f:
                    part = MIMEApplication(f.read(), Name=filename)
                    part["Content-Disposition"] = f'attachment; filename="{filename}"'
                    self.message.attach(part)

    def send_message(self):
        """Function to send email message"""
        # Create SMTP session
        print(f"Sending email to {self.receiver_email} at {current_datetime()}")
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
                server.starttls()
                server.login(self.bot_email, self.bot_pass)
                server.send_message(self.message)
            print(f"Email sent at {current_datetime()}")
        except OSError as e:
            print(f"{e}: email could not be sent")


class EmailContent:
    """Content structure for email"""

    def __init__(
        self,
        filename: str,
        conditional_string: str,
        allowed_attachments: List,
        subject: str,
        body: str = "",
    ):
        self.filename = filename
        self.conditional_string = conditional_string
        self.allowed_attachments = allowed_attachments
        self.subject = subject
        self.body = body


def send_email(email_content: EmailContent):
    """Main function to intialize email message and send to recipient"""
    eb = EmailBot()
    eb.read_file_contents(email_content.filename)

    if email_content.conditional_string not in eb.file_contents:
        # Update attachments list if files found in current directory
        eb.check_for_attachements(email_content.allowed_attachments)

    eb.create_message(subject=email_content.subject)
    eb.add_message_body(body=f"{email_content.body}{eb.file_contents}")
    eb.add_attachments()

    eb.send_message()


if __name__ == "__main__":
    test_content = EmailContent(
        filename="test.txt",
        conditional_string="not currently available",
        allowed_attachments=["test.png"],
        subject="Test Email",
    )
    EB = EmailBot()
    EB.read_file_contents(test_content.filename)

    if test_content.conditional_string not in EB.file_contents:
        EB.check_for_attachements(test_content.allowed_attachments)

    print(f"Sending test email to {EB.receiver_email} at {current_datetime()}")

    EB.create_message(subject=test_content.subject)
    EB.add_message_body(body=f"{test_content.body}{EB.file_contents}")
    EB.add_attachments()

    EB.send_message()
