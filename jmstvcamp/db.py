# encoding=latin1
import formencode
import copy
import uuid
import hashlib
import datetime
import markdown
from pymongo.son import SON

formencode.api.set_stdtranslation(domain="FormEncode", languages=["de"])

import emails

import re
import cgi

md = markdown.Markdown(safe_mode="remove")

re_string = re.compile(r'(?P<htmlchars>[<&>])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)
def plaintext2html(text, tabstop=4):
    def do_sub(m):
        c = m.groupdict()
        if c['htmlchars']:
            return cgi.escape(c['htmlchars'])
        if c['lineend']:
            return '<br>'
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;'*tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' '*tabstop;
        else:
            url = m.group('protocal')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
    return re.sub(re_string, do_sub, text)

lre_string = re.compile(r'(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)
def linkify(text):
    def do_sub(m):
        c = m.groupdict()
        if c['protocal']:
            url = m.group('protocal')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
    return re.sub(lre_string, do_sub, text)


class EmailSchema(formencode.Schema):
    email = formencode.All(formencode.validators.Email(), formencode.validators.UnicodeString(not_empty=True))

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
        pw = unicode(uuid.uuid4())[:8]
        self['password'] = hashlib.new("md5",pw).hexdigest()
        return pw

    @property
    def fmt_bio(self):
        """convert plain text bio to HTML"""
        a = md.convert(self['bio'])
        print a
        return linkify(a)

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

    def save(self, user, values):
        """save a user"""
        for a,v in values.items():
            if v is None:
                v=u""
            user[a] = v
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
        euser = emails.UserEMailAdapter(self.settings, user)
        euser.send_optin()
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

            # now send the welcome mail
            pw = user.create_pw()
            euser = emails.UserEMailAdapter(self.settings, user)
            euser.send_welcome(pw)
            user.log("welcome mail sent")
            self.coll.save(user)
            return True
        else:
            user.log("validation code NOT checked successfully")
            settings.log.info("validation code for user %s NOT checked successfully" %user['email']) 
            return False

    def send_new_password(self, user):
        """create and send a new password to a user"""
        if user['state']=="created":
            self.settings.log.warn("a new password is not supposed to be sent to users with state==created, user=%s" %user['email']) 
            return None
        pw = user.create_pw()
        euser = emails.UserEMailAdapter(self.settings, user)
        euser.send_newpw(pw)
        user.log("new password sent")
        self.coll.save(user)
