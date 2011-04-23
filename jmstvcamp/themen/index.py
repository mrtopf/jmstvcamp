# encoding=latin1
import werkzeug
import formencode
import jmstvcamp.utils as utils
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

class IndexHandler(Handler):
    """show the themen page"""

    template="programm.html"

    def get(self):
        sort_order = self.request.args.get("sort","date")
        if sort_order == "favs": 
            orig_topics1 = self.settings.db.topics.find({'voters': {'$in':self.userid}}).sort("date",-1)
            orig_topics2 = self.settings.db.topics.find({'voters': {'$in':self.userid}}).sort("date",-1)
            orig_topics = orig_topics1 + orig_topics2
        else:
            if sort_order not in ('votes', 'date'):
                sort_order = "date"
            orig_topics = self.settings.db.topics.find().sort(sort_order,-1)
        topics = []
        uid = self.userid
        for topic in orig_topics:
            topic['mine'] = topic['user']==self.userid
            topic['user'] = self.settings.users.get_by_id(topic['user'])
            topic['has_voted'] = uid in topic['voters']
            topic['fmt'] = utils.markdownify(topic['content'])
            topics.append(topic)
        
        return self.render(themen=topics, order=sort_order)
