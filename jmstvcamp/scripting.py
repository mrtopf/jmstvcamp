import sys
import os
from paste.deploy import loadapp

def get_app():
    config = sys.argv[1]
    app = loadapp('config:%s' %config,name="website")
    return app

