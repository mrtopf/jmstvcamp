#encoding=utf8
"""

EMail adapters

"""


import urlparse
import smtplib
from email.mime.text import MIMEText


class Mailer(object):
    """a real mailer"""

    def __init__(self):
        self.server = smtplib.SMTP()

    def _mail(self, fromaddr, to, subject, payload):
        msg = MIMEText(payload.encode("utf8"), 'plain', 'utf8')

        msg['Subject'] = subject
        msg['From'] = fromaddr
        msg['To'] = to

        self.server.connect()
        self.server.sendmail(fromaddr, [to], msg.as_string())
        self.server.quit()

    def mail(self, fromaddr, to, subject, payload):
        return self._mail(fromaddr, to, subject, payload)

class DummyMailer(object):
    """a dummy mailer which only stores and prints stuff"""

    def __init__(self):
        self.last_mail = {}

    def mail(self, fromaddr, to, subject, payload):
        self.last_mail = {
            'fromaddr': fromaddr,
            'to': to,
            'subject': subject,
            'payload': payload
        }
        print payload

# that you can define the mailer to use by it's name in etc/*.ini
# this is used in setup.py
MAILERS = {
    'real' : Mailer,
    'dummy' : DummyMailer,
}

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
        self.settings.mailer.mail(
                fromaddr,
                user['email'],
                subject, 
                payload
        )

        #self.settings.mailer.mail(fromaddr, user['email'], msg.as_string())

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

    def send_waitinglist(self):
        """inform a user that he is on the waitinglist"""
        self.send('Sie sind auf der Warteliste für das JMStVCamp', 'onwaitinglist.txt')

    def send_attend(self):
        """inform a user that he is attending"""
        self.send('Sie sind beim JMStVCamp auf die Teilnehmerliste nachgerückt', 'fromwaitinglist.txt')

