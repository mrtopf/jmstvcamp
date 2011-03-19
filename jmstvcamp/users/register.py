# encoding=latin1
import formencode
import werkzeug
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])
import jmstvcamp.db

class RegistrationSchema(formencode.Schema):
    name = formencode.All(formencode.validators.UnicodeString(not_empty=True))
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))
    attend = formencode.validators.OneOf(['yes','no','maybe'])


class Register(Handler):
    """Registration handler"""

    template = "registrationform.html"

    def get(self):
        return self.render(errors={}, values={}, state=None)

    def post(self):
        """register"""
        try:
            values = RegistrationSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        try:
            user = self.settings.users.create(values) 
        except jmstvcamp.db.UserExists, e:
            errors = { 'email' : 'Diese E-Mail-Adresse ist schon in der Datenbank vorhanden'}
            return self.render(errors = errors, values = self.request.form, state=e.user['state'])
    
        self.settings.users.send_validation_code(user)
        return self.redirect("/registrationsuccess.html")


