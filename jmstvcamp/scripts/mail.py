#!/usr/bin/env python
import pymongo
import sys
import os.path
from jmstvcamp import emails
from jmstvcamp import scripting
import jinja2

class PathLoader(jinja2.loaders.BaseLoader):
    """a template loader for a single path"""

    def get_source(self, environment, path):
        if not os.path.exists(path):
            raise jinja2.loaders.TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, lambda: mtime == os.path.getmtime(path)


class Mailer(object):

    def __init__(self):
        self.app = scripting.get_app()
        self.settings = self.app.settings
        self.users = self.settings.users
        self.template = jinja2.Environment(loader=PathLoader()).get_template(sys.argv[3])
        self.subject = sys.argv[2]
        self.mailer = self.settings.mailer

    def send(self):
        """send out the newsletter"""
        people = self.users.all
        for user in people:
            payload = self.template.render(user=user)
            self.mailer.mail(self.settings.fromaddr, 
                user['email'], 
                self.subject,
                payload)
            print "sent to", user['name']
        print "finished, sent out %s mails" %people.count()

if __name__=="__main__":
    mailer = Mailer()
    mailer.send()



