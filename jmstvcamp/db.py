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
        self.log = settings.log
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
        values['waitinglist'] = False # if the user is on the waiting list (only applies to attend=yes)
        values['queue_date'] = None # when the user was added to the list of attendees (only applies to attend=yes and waitinglist=True)
        values['log'] = []

        user = User(values)

        # create a password
        self.coll.save(user)
        return user

    def save(self, user, values):
        """save a user"""
        # create a new user copy
        new_user = User(copy.deepcopy(user.to_dict()))
        for a,v in values.items():
            if v is None:
                v=u""
            new_user[a] = v
        new_user = self.process_attendance(user, new_user)
        self.coll.save(new_user) # save after check because of statistics
        self.move_up() # eventually search for people on waiting list of we have space

    def process_attendance(self, old_user, new_user):
        """trigger any events which might result from a change in attendance state.
        We get the old record of the user and the new one."""
        old_attend = old_user['attend']
        new_attend = new_user['attend']
        self.log.debug("old_attend: %s, new_attend: %s" %(old_attend, new_attend))
        if old_attend == new_attend:
            return new_user # if nothing changed, nothing has to be done
        count = self.yescount # this includes the old state of the user
        self.log.debug("count: %s, maxpeople: %s" %(count, self.settings.maxpeople))
        if count < self.settings.maxpeople:
            # clear any attendance metadata
            new_user['queue_date'] = None
            new_user['waitinglist'] = False
            return new_user # nothing to be done if we have less people than allowed 
        
        if new_attend == "yes": 
            # user changed to yes and thus needs to get onto the waiting list
            new_user['queue_date'] = datetime.datetime.now()
            new_user['waitinglist'] = True
            new_user.log("user added to waiting list")
            euser = emails.UserEMailAdapter(self.settings, new_user)
            euser.send_waitinglist()
            return new_user
        elif old_attend == "yes":
            # user was attending but now isn't anymore
            new_user.log("user removed from attending or waiting list")
        new_user['queue_date'] = None
        new_user['waitinglist'] = False
        return new_user

    def move_up(self):
        """check if people can move up to attendance"""
        count = self.yescount # people attending
        self.log.debug("moveup: count = %s, maxcount = %s" %(count, self.settings.maxpeople))
        if count >= self.settings.maxpeople:
            return # nothing to do
        
        # find people on the waitinglist
        diff = self.settings.maxpeople - count
        users = self.coll.find(
                    {'state' : 'live', 
                     'attend' : 'yes',
                     'waitinglist' : True},
                 sort=[('queue_date', 1)], as_class=User).limit(diff)
        
        for user in users:
            user['queue_date'] = None
            user['waitinglist'] = False
            user.log("move up from waitinglist")
            self.log.info("user %s moved from waitinglist" %user['_id'])
            euser = emails.UserEMailAdapter(self.settings, user)
            euser.send_attend()
            self.coll.save(user)

    def get(self, email):
        """retrieve a user by email or return None"""
        return self.coll.find_one({'email' : email}, as_class=User)

    def get_by_code(self, code):
        """retrieve a user by code or return None"""
        return self.coll.find_one({'validationcode' : code}, as_class=User)

    def get_by_id(self, _id):
        """retrieve a user by code or return None"""
        return self.coll.find_one({'_id' : _id}, as_class=User)

    def get_attend(self, attend="yes"):
        """return a list by attendance status"""
        q = {'attend' : attend, 'state' : 'live'}
        res = self.coll.find(q, as_class=User)
        return res

    @property
    def yescount(self):
        """return the number of people attending and not on waitinglist"""
        q = {'attend' : "yes", 'state' : 'live', 'waitinglist' : False}
        return self.coll.find(q).count()

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

            # check if the user needs to go on the waitinglist
            if self.yescount >= self.settings.maxpeople and user['attend']=="yes":
                self.settings.log.info("User %s goes to the waiting list" %user['_id'])
                user['queue_date'] = datetime.datetime.now()
                user['waitinglist'] = True

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
