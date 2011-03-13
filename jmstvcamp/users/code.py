# encoding=latin1
import werkzeug
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

import jmstvcamp.db

class NewCode(Handler):
    """validate a token"""

    def get(self):
        return self.render()

    @html
    def render(self, errors={}, values={}, state="none"):
        tmpl = self.settings.pts.get_template("newcode.html")
        return tmpl.render(errors=errors, values=values, state=state)
    
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

        self.settings.users.send_validation_code(user)
        return werkzeug.redirect(location="/newcode_success.html")



