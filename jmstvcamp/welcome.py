# encoding=latin1
import werkzeug
from framework import Handler
from framework.decorators import html

class Welcome(Handler):
    """Welcome handler"""

    template="welcome.html"

    def get(self):
        return self.render()

