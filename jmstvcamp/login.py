# encoding=latin1
import formencode
import werkzeug
import urlparse
from framework import Handler
from framework.decorators import html

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])
import db

class LoginSchema(formencode.Schema):
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))
    password = formencode.validators.String(not_empty=True)

class Login(Handler):
    """Login handler"""

    def get(self):
        return self.render()

    @html
    def render(self, errors={}, values={}):
        tmpl = self.settings.pts.get_template("login.html")
        return tmpl.render(errors=errors, values=values)

    def error(self, field, error, values):
        errors = { field: error }
        return self.render(errors, values)

    def post(self):
        """register"""
        try:
            values = LoginSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        user = self.settings.users.get(values['email'])
        if user is None:
            return self.error("email", "Ein Benutzer mit dieser E-Mail-Adresse existiert nicht in der Datenbank", values)

        if user['state']=="created":
            return self.error("email", "Dieser Benutzer ist noch nicht aktiviert.", values)

        if user['state']!="live":
            return self.error("email", "Dieser Benutzer ist noch nicht aktiviert.", values)

        if not user.checkpw(values['password']):
            return self.error("password", "Dieses Passwort ist leider falsch.", values)

        # user ok, log him in.
        url = urlparse.urljoin(self.settings.virtual_host,"/user/profile")
        res = werkzeug.redirect(location=url)
        cv = self.get_user_cookie(user)
        res.set_cookie("u", cv)
        return res

class Logout(Handler):
    """log the user out (= clear cookie)"""

    def get(self):
        """logout"""
        url = urlparse.urljoin(self.settings.virtual_host,"/")
        res = werkzeug.redirect(location=url)
        res.delete_cookie("u")
        return res








