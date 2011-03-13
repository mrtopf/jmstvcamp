# encoding=latin1
import formencode
import werkzeug
import copy
import pwtools
import uuid
import hashlib
import datetime
from pymongo.son import SON
from framework import Handler
from framework.decorators import html

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])

import emails

class User(SON):
    """a user object"""

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        g = pwtools.PasswordGenerator()
        self.plainpw = g.generate()
        if not self.has_key('_id'):
            self['_id'] = hashlib.new('md5',self['email']).hexdigest()
        # TODO: move password to validation creation as well (and call it init_user(), move it to handler again?)
        self['password'] = hashlib.new("md5",self.plainpw).hexdigest()
        self['state'] = "created" # no optin yet
        self['created'] = datetime.datetime.now()
        self['log'] = []

    def checkpw(self, password):
        """check if the given password is valid"""
        checkhash = hashlib.new("md5",password).hexdigest()
        return checkhash==self['password']

    def log(self, msg):
        entry = {
            'date' : datetime.datetime.now(),
            'msg' : msg
        }
        self['log'].append(entry)

    def send_validation(self, settings):
        """send a validation code to a user"""
        if self['state']!="created":
            settings.log.warn("a validation code is not supposed to be sent to users with state!=created, user=%s" %self['email']) 
            return
        self['validationcode'] = unicode(uuid.uuid4())
        self['validationcode_sent'] = datetime.datetime.now()
        euser = emails.UserEMailAdapter(settings, self)
        euser.send_optin()
        self.log("validation code sent")

    def validate(self, settings, code):
        """check the validation code and change the state. Returns ``True`` for
        success and ``False`` for failure (wrong code)"""
        if self['state']!="created":
            settings.log.warn("a validation code is not supposed to be checked to users with state!=created, user=%s" %self['email']) 
            return
        if self['validationcode'] == code:
            self['state'] = "live"
            self['validationcode'] = None
            self.log("validation code checked successfully")
            settings.log.info("validation code for user %s checked successfully" %self['email']) 
            return True
        else:
            self.log("validation code NOT checked successfully")
            settings.log.info("validation code for user %s NOT checked successfully" %self['email']) 
            return False

class RegistrationSchema(formencode.Schema):
    name = formencode.All(formencode.validators.UnicodeString(not_empty=True))
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))
    attend = formencode.validators.OneOf(['yes','no','maybe'])

class ProfileSchema(RegistrationSchema):
    organization = formencode.All(formencode.validators.PlainText())
    homepage = formencode.validators.URL()
    twitter = formencode.validators.PlainText()

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
            values = RegistrationSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        # check if the email address is already in the database
        email = values['email']
        user = self.settings.userdb.find_one({'email' : email})
        if user is not None:
            errors = {
                'email' : 'Diese E-Mail-Adresse ist schon in der Datenbank vorhanden'
            }
            # TODO: Ask user to resend validation code or password
            return self.render(errors, self.request.form, state=user['state'])
    
        user = User(copy.copy(values))
        user.send_validation(self.settings)
        self.settings.userdb.save(user)
        return werkzeug.redirect(location="/registrationsuccess.html")

class Validate(Handler):
    """validate a token"""

    @html
    def wrong(self):
        """show the wrong code page"""
        return self.settings.pts.get_template("wrongcode.html").render()

    def get(self):
        """check the validation code"""
        code = self.request.args.get("token", None)
        if code is None:
            self.settings.log.warn("validation: no code found in request")
            return self.wrong()
        user = self.settings.userdb.find_one({'validationcode' : code}, as_class=User)
        if user is None:
            self.settings.log.warn("validation: user not found for code %s" %code)
            return self.wrong()
        if user['state']!="created":
            self.settings.log.warn("validation: user %s has wrong state %s" %(user['email'], user['state']))
            return self.wrong()
        
        res = user.validate(self.settings,code)
        self.settings.userdb.save(user)
        if not res:
            self.settings.log.warn("validation failed for user %s and code %s" %(user['email'], code))
            return self.wrong()

        # set the login cookie and redirect to the profile page
        url = urlparse.urljoin(self.settings.virtual_host,"/profile")
        res = werkzeug.redirect(location=url)
        res.set_cookie("t", self.token)
        return res




