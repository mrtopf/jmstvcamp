# encoding=latin1
import formencode
import werkzeug
import copy
import pwtools
import uuid
import hashlib
import datetime
from pymongo.son import SON
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])
import jmstvcamp.db

class Register(Handler):
    """Registration handler"""

    def get(self):
        return self.render()

    @html
    def render(self, errors={}, values={}, state="none"):
        tmpl = self.settings.pts.get_template("registrationform.html")
        return tmpl.render(errors=errors, values=values, state=state)

    def post(self):
        """register"""
        try:
            values = jmstvcamp.db.RegistrationSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        try:
            user = self.settings.users.create(values) 
        except jmstvcamp.db.UserExists, e:
            errors = { 'email' : 'Diese E-Mail-Adresse ist schon in der Datenbank vorhanden'}
            return self.render(errors = errors, values = self.request.form, state=e.user['state'])
    
        self.settings.users.send_validation_code(user)
        return werkzeug.redirect(location="/registrationsuccess.html")
