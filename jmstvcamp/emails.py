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

    def send(self, subject, tmplname, **kwargs):
        """send a mail to the user with the given ``subject``, the given
        ``from`` address, a JINJA2 template to use in ``tmplname`` and
        optional arguments passed to that template"""
        user = self.context
        fromaddr = self.settings.fromaddr

        # prepare params
        params = {
            'user': user
        }
        params.update(kwargs)

        # render template
        tmpl = self.settings.email_templates.get_template(tmplname)
        payload = tmpl.render(params)

        # encode it in a message
        msg = MIMEText(payload.encode("utf8"), 'plain', 'utf8')

        msg['Subject'] = subject
        msg['From'] = fromaddr
        msg['To'] = user['email']

        s = smtplib.SMTP()
        s.connect()
        s.sendmail(fromaddr, [user['email']], msg.as_string())
        s.quit()


    def send_optin(self):
        """send the opt-in message to the user"""
        self.send('Bitte bestätigen Sie Ihre Anmeldung zum JMStVCamp', 'optin.txt', 
            url = urlparse.urljoin(self.settings.virtual_host,"/user/validate?token="+self.context['validationcode'])
        )

    def send_welcome(self, pw):
        """send the welcome message"""
        self.send('Willkommen beim JMStVCamp', 'welcome.txt', pw =  pw )

    def send_newpw(self, pw):
        """send the new password message"""
        self.send('Ihr neues Passwort für das JMStVCamp', 'newpw.txt', pw =  pw )

    def send_newcode(self, pw):
        """send the new validation code"""
        self.send('Ihr neuer Validierungscode für das JMStVCamp', 'newcode.txt', 
            url = urlparse.urljoin(self.settings.virtual_host,"/user/validate?token="+self.context['validationcode'])
        )

