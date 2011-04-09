# encoding=latin1
import werkzeug
import datetime
import uuid
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, logged_in

class NewHandler(Handler):
    """add a new topic"""

    @logged_in()
    def post(self):
        content = self.request.form.get("content","")
        if content == "" or content is None:
            return self.redirect("/themen/")

        # add a new topic
        topic = {
            '_id' : unicode(uuid.uuid4()),
            'content' : content,
            'votes' : 1,
            'voters' : [self.user['_id'],],
            'user' : self.user['_id'],
            'date' : datetime.datetime.now(),
        }
        self.settings.db.topics.save(topic)
        return self.redirect("/themen/")



