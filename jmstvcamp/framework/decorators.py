"""
some useful decorators
"""

import werkzeug
import functools
import json as simplejson
import datetime
import werkzeug.exceptions

def jsonconverter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj))


def html(method):
    """takes a string output of a view and wraps it into a text/html response"""
    
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        response = werkzeug.Response(method(*args, **kwargs))
        response.content_type = "text/html; charset=utf-8"
        return response

    return wrapper

class json(object):
    
    def __init__(self, **headers):
        self.headers = {}
        for a,v in headers.items():
            ps = a.split("_")
            ps = [p.capitalize() for p in ps]
            self.headers["-".join(ps)] = v
    
    def __call__(self, method):
        """takes a dict output of a handler method and returns it as JSON"""

        that = self
    
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            data = method(self, *args, **kwargs)
            s = simplejson.dumps(data, default = jsonconverter)
            if self.request.args.has_key("callback"):
                callback = self.request.args.get("callback")
                s = "%s(%s)" %(callback, s)
                response = werkzeug.Response(s)
                response.content_type = "application/javascript"
            else:
                response = werkzeug.Response(s)
                response.content_type = "application/json"
            for a,v in that.headers.items():
                response.headers[a] = v
            return response

        return wrapper

class logged_in(object):                                                                                                                                                        
    """check if a valid user is present"""
    def __call__(self, method):
        """check user"""

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.user is None:
                raise werkzeug.exceptions.Unauthorized()
            return method(self, *args, **kwargs)
        return wrapper

