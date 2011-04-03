# encoding=latin1
import werkzeug
from framework import Handler
from framework.decorators import html

class Participants(Handler):
    """show participants"""

    template="participants.html"

    def get(self):
        db = self.settings.users
        yes = [u for u in db.get_attend("yes") if not u['waitinglist']]
        waiting = [u for u in db.get_attend("yes") if u['waitinglist']]
        maybe = db.get_attend("maybe") 
        no = db.get_attend("no") 
        return self.render(yes = yes, maybe = maybe, no=no, waiting=waiting)

