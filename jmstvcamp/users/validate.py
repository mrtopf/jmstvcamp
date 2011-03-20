# encoding=latin1
import werkzeug
import copy
import uuid
import hashlib
import datetime
import urlparse
from pymongo.son import SON
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

import jmstvcamp.db

class Validate(Handler):
    """validate a token"""

    @html
    def wrong(self):
        """show the wrong code page"""
        return self.render("wrongcode.html")

    def get(self):
        """check the validation code"""
        code = self.request.args.get("token", None)
        if code is None:
            self.settings.log.warn("validation: no code found in request")
            return self.wrong()
        user = self.settings.users.get_by_code(code)
        if user is None:
            self.settings.log.warn("validation: user not found for code %s" %code)
            return self.wrong()
        if user['state']!="created":
            self.settings.log.warn("validation: user %s has wrong state %s" %(user['email'], user['state']))
            return self.wrong()
        
        res = self.settings.users.validate_code(code)
        if not res:
            self.settings.log.warn("validation failed for user %s and code %s" %(user['email'], code))
            return self.wrong()

        # set the login cookie and redirect to the profile page
        url = urlparse.urljoin(self.settings.virtual_host,"/welcome")
        res = self.redirect(url)
        cv = self.get_user_cookie(user)
        res.set_cookie("u", cv)
        return res




