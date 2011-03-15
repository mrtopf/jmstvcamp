from framework import Handler, Application
from framework.decorators import html
from logbook import Logger
from logbook import FileHandler
import werkzeug
from jinja2 import Environment, PackageLoader, TemplateNotFound
import formencode

import setup
import users
import login

class StaticHandler(Handler):
    def get(self, path_info):
        return self.settings.staticapp

class Page(Handler):
    """show a page"""

    @html
    def get(self, page=None):
        if page is None:
            page = "index.html"
        try:
            tmpl = self.settings.pts.get_template(page)
        except TemplateNotFound:
            print "not found", page
            raise werkzeug.exceptions.NotFound()
        out = tmpl.render()
        return out


class App(Application):

    logfilename = "/tmp/jmstvcamp.log"
    
    def setup_handlers(self, map):
        """setup the mapper"""
        map.connect(None, "/login", handler=login.Login)
        map.connect(None, "/css/{path_info:.*}", handler=StaticHandler)
        map.connect(None, "/js/{path_info:.*}", handler=StaticHandler)
        map.connect(None, "/img/{path_info:.*}", handler=StaticHandler)
        map.connect(None, "/", handler=Page)
        map.connect(None, "/{page}", handler=Page)

        users.setup_handlers(map)




def main():
    port = 7653
    app = App(setup.setup())
    return webserver(app, port)

def frontend_factory(global_config, **local_conf):
    settings = setup.setup(**local_conf)
    return App(settings)

def webserver(app, port):
    import wsgiref.simple_server
    wsgiref.simple_server.make_server('', port, app).serve_forever()

if __name__=="__main__":
    main()

