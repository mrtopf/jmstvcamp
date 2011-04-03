import werkzeug
import formencode
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, logged_in

import jmstvcamp.db

class ChangeState(Handler):
    """change the attendance state of a user"""

    @logged_in()
    def post(self):
        """change state"""
        values = { 'attend' : self.request.form['attend'] }
        user = self.settings.users.save(self.user, values) 
        return self.redirect("/teilnehmer.html")


