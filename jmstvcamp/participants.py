# encoding=latin1
import werkzeug
from framework import Handler
from framework.decorators import html

class Participants(Handler):
    """show participants"""

    template="participants.html"

    def get(self):
        db = self.settings.users
        yes = db.get_attend("yes")
        maybe = db.get_attend("maybe") 
        no = db.get_attend("no") 
        return self.render(yes = yes, maybe = maybe, no=no)

