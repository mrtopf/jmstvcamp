# encoding=latin1
import werkzeug
from framework import Handler
from framework.decorators import html

class Participants(Handler):
    """show participants"""

    template="participants.html"

    def get(self):
        db = self.settings.users
        yes = self.settings.users.coll.find(
                {'attend' : "yes", 'state' : 'live', "waitinglist":False},
                sort=[('name',1)])
        waiting = self.settings.users.coll.find(
                {'attend' : "yes", 'state' : 'live', "waitinglist":True},
                sort=[('name',1)])
        maybe = self.settings.users.coll.find(
                {'attend' : "maybe", 'state' : 'live'},
                sort=[('name',1)])
        no = self.settings.users.coll.find(
                {'attend' : "no", 'state' : 'live'},
                sort=[('name',1)])
        count = self.settings.maxpeople
        return self.render(yes = yes, maybe = maybe, no=no, waiting=waiting, 
                    count=count)

