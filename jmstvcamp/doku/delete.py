# encoding=latin1
import werkzeug
import formencode
import uuid
import datetime
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, logged_in

class DeleteHandler(Handler):
    """delete a pad"""

    @logged_in()
    def get(self, pid=None):
        pad = self.settings.db.pads.find_one({'_id':pid})
        if pad is None:
            return self.redirect("/doku/")
        if pad['user']!=self.userid:
            return self.redirect("/doku/")
        
        self.settings.db.pads.remove({'_id':pid})
        return self.redirect("/doku/")

