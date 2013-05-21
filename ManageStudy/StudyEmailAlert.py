import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

# Import smtplib for the actual sending function
import smtplib

# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def send_email(To=[], From='', subject='', preamble='', attachment_paths=[]):
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    # me == the sender's email address
    msg['From'] = From
    msg['To'] = ', '.join(To)
    msg.preamble = preamble

    for attachment in attachment_paths:
        part = MIMEBase('application', "octet-stream")
        fp = open(attachment, 'rb')
        part.set_payload(fp.read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(attachment)))
        msg.attach(part)
        fp.close()


    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail('nsc2124@columbia.edu', To, msg.as_string())
    s.quit()
