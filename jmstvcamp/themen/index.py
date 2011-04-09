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
        orig_topics = self.settings.db.topics.find().sort("date",-1)
        topics = []
        uid = self.userid
        for topic in orig_topics:
            topic['mine'] = topic['user']==self.userid
            topic['user'] = self.settings.users.get_by_id(topic['user'])
            topic['has_voted'] = uid in topic['voters']
            topic['fmt'] = utils.markdownify(topic['content'])
            topics.append(topic)
        
        return self.render(themen=topics)
