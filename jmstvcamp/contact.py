# encoding=latin1
import formencode
from framework import Handler
from framework.decorators import html
import smtplib
from email.mime.text import MIMEText

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])

class ContactSchema(formencode.Schema):
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))
    content = formencode.validators.String(not_empty=True)

class Contact(Handler):
    """contact handler"""

    template="kontakt.html"

    def get(self):
        return self.render(errors={}, values={})

    def post(self):
        """register"""
        try:
            values = ContactSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        # send the email
        msg = MIMEText(values['content'].encode("utf8"), 'plain', 'utf8')

        msg['Subject'] = "Nachricht zum JMStVCamp"
        msg['To'] = self.settings.fromaddr
        msg['From'] = values['email']
        print msg.as_string()

        s = smtplib.SMTP()
        s.connect()
        s.sendmail(values['email'], [self.settings.fromaddr], msg.as_string())
        s.quit()

        return self.redirect("/kontakt_success.html")

