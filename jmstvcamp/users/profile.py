# encoding=latin1
import werkzeug
import copy
import uuid
import hashlib
import datetime
import urlparse
from pymongo.son import SON
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, logged_in

import jmstvcamp.db

class Profile(Handler):
    """show a user profile"""

    @html
    def get(self, username=None):
        """display a user profile"""
        ownprofile = False
        if username is None:
            # try to use the logged in user if existing
            user = self.user
            if user is None:
                raise werkzeug.exceptions.NotFound()
        else:
            user = self.settings.users.get_by_id(username)
            if user is None:
                raise werkzeug.exceptions.NotFound()
       
        if self.user is not None:
            ownprofile = self.user['_id'] == user['_id']

        # collect data
        tmpl = self.settings.pts.get_template("profile.html")
        return tmpl.render(
                user = user, 
                ownprofile = ownprofile)


class Edit(Handler):
    """show the profile edit page for logged in users"""

    @logged_in()
    def get(self):
        return self.render()

    @html
    def render(self, errors={}, values={}, state="none"):
        tmpl = self.settings.pts.get_template("editform.html")
        return tmpl.render(errors=errors, values=values, state=state)
