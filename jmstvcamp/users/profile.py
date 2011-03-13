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

class Profile(Handler):
    """show a user profile"""

    @html
    def get(self, user=None):
        """display a user profile"""
        if user is None:
            user = self.user
        if user is None:
            # TODO: proper error handling
            return None
        
        # collect data
        tmpl = self.settings.pts.get_template("profile.html")
        return tmpl.render(user = user)


