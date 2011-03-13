# encoding=latin1
import formencode
import copy
import pwtools
import uuid
import hashlib
import datetime
from pymongo.son import SON

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])

import emails

class EmailSchema(formencode.Schema):
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))

class RegistrationSchema(formencode.Schema):
    name = formencode.All(formencode.validators.UnicodeString(not_empty=True))
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))
    attend = formencode.validators.OneOf(['yes','no','maybe'])

class ProfileSchema(RegistrationSchema):
    organization = formencode.All(formencode.validators.PlainText())
    homepage = formencode.validators.URL()
    twitter = formencode.validators.PlainText()

class ValidationError(Exception):
    """raise a validation error"""

    def __init__(self, field, msg):
        self.field = field
        self.msg = msg

class UserExists(Exception):
    """raised if a user already exists"""

    def __init__(self, user):
        self.user = user

class User(SON):
    """a user object"""

    def checkpw(self, password):
        """check if the given password is valid"""
        checkhash = hashlib.new("md5",password).hexdigest()
        return checkhash==self['password']

    def create_pw(self):
        """create a password"""
        g = pwtools.PasswordGenerator()
        pw = g.generate()
        self['password'] = hashlib.new("md5",pw).hexdigest()
        return pw

    def log(self, msg):
        entry = {
            'date' : datetime.datetime.now(),
            'msg' : msg
        }
        self['log'].append(entry)

    def create_validation_code(self):
        """create a new validation code"""
        code = self['validationcode'] = unicode(uuid.uuid4())
        self['validationcode_sent'] = datetime.datetime.now()
        self.log("validation code created")
        return code



class Users(object):
    """handle users"""

    def __init__(self, settings):
        self.settings = settings
        self.coll = settings.db[settings.usercoll]

    def create(self, values):
        """create a new user"""

        # check if the email address is already in the database
        email = values['email']
        user = self.get(email)
        if user is not None:
            raise UserExists(user)
            raise UserExists('email', 'Diese E-Mail-Adresse ist schon in der Datenbank vorhanden')

        values['_id'] = hashlib.new('md5',values['email']).hexdigest()
        values['state'] = "created" # no optin yet
        values['created'] = datetime.datetime.now()
        values['log'] = []

        user = User(values)

        # create a password
        self.coll.save(user)
        return user

    def get(self, email):
        """retrieve a user by email or return None"""
        return self.coll.find_one({'email' : email}, as_class=User)

    def get_by_code(self, code):
        """retrieve a user by code or return None"""
        return self.coll.find_one({'validationcode' : code}, as_class=User)

    def get_by_id(self, _id):
        """retrieve a user by code or return None"""
        return self.coll.find_one({'_id' : _id}, as_class=User)

    def send_validation_code(self, user):
        """create and send a validation code and a password to a user"""
        if user['state']!="created":
            self.settings.log.warn("a validation code is not supposed to be sent to users with state!=created, user=%s" %user['email']) 
            return None
        code = user.create_validation_code()
        pw = user.create_pw()
        euser = emails.UserEMailAdapter(self.settings, user)
        euser.send_optin(pw)
        user.log("validation code %s sent" %code)
        self.coll.save(user)

    def validate_code(self, code):
        """check the validation code and change the state. Returns ``True`` for
        success and ``False`` for failure (wrong code)"""
        user = self.get_by_code(code)
        if user['state']!="created":
            settings.log.warn("a validation code is not supposed to be checked to users with state!=created, user=%s" %user['email']) 
            return
        if user['validationcode'] == code:
            user['state'] = "live"
            user['validationcode'] = None
            user.log("validation code checked successfully")
            self.settings.log.info("validation code for user %s checked successfully" %user['email']) 
            self.coll.save(user)
            return True
        else:
            user.log("validation code NOT checked successfully")
            settings.log.info("validation code for user %s NOT checked successfully" %user['email']) 
            return False


