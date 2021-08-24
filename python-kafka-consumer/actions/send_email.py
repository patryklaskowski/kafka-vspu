"""
vspu.ibm@gmail.com

1) Zarządzaj kontem Google > Bezpieczeństwo > Logowanie się w Google > Weryfikacja dwuetapowa > Wł.
2) Zarządzaj kontem Google > Bezpieczeństwo > Logowanie się w Google > Hasła do aplikacji > Wygeneruj
"""

import smtplib
import os

from datetime import datetime
from email.message import EmailMessage

user = os.getenv('EMAIL_ADDR')
psswd = os.getenv('EMAIL_PSSWD')  # Gmail app passwd

date_format = '%m/%d/%Y %H:%M:%S'


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)

    msg['subject'] = subject
    msg['to'] = to
    msg['from'] = user

    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    server.login(user=user, password=psswd)

    server.send_message(msg)
    server.quit()

    print(f'[{datetime.now().strftime(date_format)}] Email sent to {to}')


if __name__ == '__main__':

    email_alert(subject='VSPU Email Notification',
                body='Hello World!\nSent from automatic VSPU notification System',
                to='patryk.jacek.laskowski@gmail.com')
