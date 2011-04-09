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
    def post(self, tid=None, vote="no"):
        topic = self.settings.db.topics.find_one({'_id':tid})
        myvote = topic['voters'][self.user['_id']]
        if vote=="up" and myvote<1:
            myvote=myvote+1
        if vote=="down" and myvote>-1:
            myvote=myvote-1
        topic['voters'][self.user['_id']] = myvote
        # recompute all votes
        topic['votes'] = reduce(lambda a,b: a+b, topic['voters'].values(), 0)
        self.settings.db.topics.save(topic)
        return {'votes' : topic['votes'], 
                'myvote' : myvote
                }



