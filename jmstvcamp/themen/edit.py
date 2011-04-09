# encoding=latin1
import werkzeug
import datetime
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, logged_in

class EditHandler(Handler):
    """edit a new topic"""

    @logged_in()
    def post(self, tid):
        topic = self.settings.db.topics.find_one({'_id':tid})
        if topic['user']!=self.userid:
            return self.redirect("/themen/")
        content = self.request.form.get("content","")
        if content == "" or content is None:
            return self.redirect("/themen/")

        topic['content'] = content
        self.settings.db.topics.save(topic)
        return self.redirect("/themen/")



