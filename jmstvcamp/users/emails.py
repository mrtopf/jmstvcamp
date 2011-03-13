#encoding=utf8
"""

EMail adapters

"""


import urlparse
import smtplib
from email.mime.text import MIMEText


class Adapter(object):
    """a simple adapter"""

    def __init__(self, settings, context):
        self.context = context
        self.settings = settings

class UserEMailAdapter(Adapter):

    def send_optin(self, pw=None):
        """send the opt-in message to the user"""

        user = self.context
        params = {
            'user': user, 
            'pw': pw, 
            'url' : urlparse.urljoin(self.settings.virtual_host,"/user/validate?token="+self.context['validationcode'])
        }

        tmpl = self.settings.email_templates.get_template("optin.txt")

        payload = tmpl.render(params)
        print payload
        msg = MIMEText(payload.encode("utf8"), 'plain', 'utf8')

        msg['Subject'] = 'Bitte bestätigen Sie Ihre Anmeldung zum JMStVCamp'
        msg['From'] = "info@jmstvcamp.de"
        msg['To'] = user['email']

        # Send the message via our own SMTP server, but don't include the
        # # envelope header.
        s = smtplib.SMTP()
        s.connect()
        s.sendmail("info@jmstvcamp.de", [user['email']], msg.as_string())
        s.quit()


