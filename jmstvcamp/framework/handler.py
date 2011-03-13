import os
import json as simplejson
from paste.urlparser import StaticURLParser
from paste.fileapp import FileApp
import werkzeug.exceptions
from paste.auth import auth_tkt

from context import PageContext

class Handler(object):
    """a request handler which is also the base class for an application"""
    
    def __init__(self, app=None, request=None, settings={}):
        """initialize the Handler with the calling application and the request
        it has to handle."""
        
        self.app = app
        self.request = request
        self.settings = settings
        self.userid = None
        if self.request.cookies.has_key("t"):
            self.settings.log.debug("found token in cookie")
            at = self.request.cookies['t']
            try:
                self.timestamp, self.userid, self.roles, self.token_attribs = auth_tkt.parse_ticket(self.settings.shared_secret, at, "127.0.0.1")
            except auth_tkt.BadTicket, e:
                self.settings.log.error("BAD token detected: %s " %e)
                pass
        if self.userid is not None:
            self.user = self.settings.userdb.find_one({'_id' : self.userid})
            if self.user is None:
                self.settings.log.error("user in token not found: %s " %self.userid)
        # TODO: set an empty cookie and redirect to homepage on errors

    def set_user(self, user):
        """store a user in a cookie"""


    def handle(self, **m):
        """handle a single request. This means checking the method to use, looking up
        the method for it and calling it. We have to return a WSGI application"""
        method = self.request.method.lower()
        if hasattr(self, method):
            #self.settings.log.debug("calling method %s on handler '%s' " %(self.request.method, m['handler']))
            del m['handler']
            return getattr(self, method)(**m)
        else:
            return werkzeug.exceptions.MethodNotAllowed()
        
    @property
    def context(self):
        """returns a AttributeMapper of default variables to be passed to templates such as the
        base CSS and JS components. It can be overridden in subclasses and appended to in views for 
        different templates.
        
        For instance you can do the following::
        
            return self.app.settings.templates['templates/master.pt'].render(
                something = "foobar",
                **self.tmpl_params
            )

        """
        
        d = dict(
            handler = self,
            #jslinks = self.settings['js_resources'](),
            #csslinks = self.settings['css_resources'](),
            virtual_path = self.settings.virtual_path,
        )
        return PageContext(d)

class StaticHandler(Handler):
    """a handler for static files. It usually will be instantiated by the :class:`StaticHandlerFactory`.
    """
    
    def __init__(self, filepath=None, **kw):
        self.filepath = filepath
        super(StaticHandler, self).__init__(**kw)
    
    def get(self, path_info):
        return FileApp(os.path.join(self.filepath,path_info))
        
        
class StaticHandlerFactory(object):
    """a Handler factory for static resources such as JS, CSS and template files.
    You need to initialize it with the path to the directory you want to serve"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        
    def __call__(self, **kw):
        return StaticHandler(filepath = self.filepath, **kw)


class RESTfulHandler(Handler):
    """a handler for handling RESTful services. 

    Additional features:

    * adjusts the method according to a ``_method`` paramater
    * extracts the access token from the requests
    * retrieves the session from the session store/component
    """
    
    def __init__(self, **kw):
        """initialize RESTful handler by checking access token and session"""
        super(RESTfulHandler, self).__init__(**kw)
        at = None
        # check header for oauth token
        # TODO
        # check URI parameters
        ct = self.request.content_type
        if ct is None:
            ct=""
        if ct.startswith("application/json"):
            d = simplejson.loads(self.request.data)
            at = d.get("oauth_token", None)
        else:
            # TODO: Split GET and POST!
            at = self.request.values.get("oauth_token", None)
        if at is None:
            self.session = None
        else:
            am = self.settings.authmanager
            self.session = am.get(at)

    def handle(self, **m):
        """handle a single request. This means checking the method to use, looking up
        the method for it and calling it. We have to return a WSGI application"""
        method = self.request.method.lower()
        if hasattr(self, method):
            self.settings.log.debug("calling method %s on handler '%s' " %(self.request.method, m['handler']))
            del m['handler']
            return getattr(self, method)(**m)
        else:
            return werkzeug.exceptions.MethodNotAllowed()
        
