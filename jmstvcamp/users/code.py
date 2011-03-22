# encoding=latin1
import werkzeug
import formencode
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

import jmstvcamp.db

class NewCode(Handler):
    """validate a token"""

    template="newcode.html"

    def get(self):
        if self.request.args.has_key("email"):
            try:
             values = jmstvcamp.db.EmailSchema.to_python(self.request.args)
            except formencode.validators.Invalid, e:
                return self.render(errors=e.error_dict, values=self.request.form)
            return self.process(values)
        return self.render(errors={}, values={}, state=None)

    def process(self, values):
        user = self.settings.users.get(values['email'])
        if user is None:
            errors = {'email' : 'Ein Benutzer mit dieser E-Mail-Adresse ist uns nicht bekannt.'}
            return self.render(errors=errors, values=self.request.form)
        self.settings.users.send_validation_code(user)
        return self.redirect("/newcode_success.html")

    def post(self):
        """register"""
        try:
            values = jmstvcamp.db.EmailSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)
        return self.process(values)


class NewPassword(Handler):
    """send a new password to a user"""

    template="newpw.html"

    def get(self):
        return self.render(errors={}, values={}, state=None)

    def post(self):
        """register"""
        try:
            values = jmstvcamp.db.EmailSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        user = self.settings.users.get(values['email'])
        if user is None:
            errors = {'email' : 'Ein Benutzer mit dieser E-Mail-Adresse ist uns nicht bekannt.'}
            return self.render(errors=errors, values=self.request.form)

        self.settings.users.send_new_password(user)
        return self.redirect("/newpw_success.html")



