# encoding=latin1
import werkzeug
import formencode
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html

class IndexHandler(Handler):
    """show the themen page"""

    template="programm.html"

    def get(self):
        orig_topics = self.settings.db.topics.find().sort("date",-1)
        topics = []
        for topic in orig_topics:
            topic['user'] = self.settings.users.get_by_id(topic['user'])
            topic['show_up'] = topic['voters'][self.user['_id']]<1
            topic['show_down'] = topic['voters'][self.user['_id']]>-1
            topics.append(topic)
        
        return self.render(themen=topics)
