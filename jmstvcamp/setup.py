import sys
import os
import pkg_resources
import logbook
import datetime
import pymongo

from jinja2 import Environment, PackageLoader, TemplateNotFound

from quantumcore.storages import AttributeMapper
from framework.utils import get_static_urlparser
import db

def setup(**kw):
    """initialize the setup"""
    settings = AttributeMapper()
    settings['staticapp'] = get_static_urlparser(pkg_resources.resource_filename(__name__, 'static'))
    
    settings['secret_key'] = "ccdhsiuccdhsiuhhci28228zs7s8c6c8976c89c7s6s8976cs87d6" #os.urandom(20)
    settings['log'] = logbook.Logger("jmstvcamp")
    settings['dbname'] = "jmstvcamp"
    settings['shared_secret'] = "c6cs8cd67c8s76c9cs76ds98c76scds"
    settings['usercoll'] = "users"
    settings.update(kw)

    settings.pts = Environment(loader=PackageLoader("jmstvcamp","pages"))
    settings.email_templates = Environment(loader=PackageLoader("jmstvcamp","email_templates"))

    settings.db = pymongo.Connection()[settings.dbname]
    settings.userdb = settings.db[settings.usercoll]
    settings.users = db.Users(settings)
    return settings

