# encoding=latin1
import werkzeug
import datetime
import uuid
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, json, logged_in

class VoteHandler(Handler):
    """add a new topic"""

    @logged_in()
    @json()
    def post(self, tid=None):
        topic = self.settings.db.topics.find_one({'_id':tid})
        voted = self.userid in topic['voters']
        if voted:
            topic['voters'].remove(self.userid)
        else:
            topic['voters'].append(self.userid)
        topic['votes'] = len(topic['voters'])
          
        self.settings.db.topics.save(topic)
        return {'votes' : topic['votes'], 
                'myvote' : not voted
                }



