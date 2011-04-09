# encoding=latin1
import werkzeug
import formencode
import uuid
import datetime
from jmstvcamp.framework import Handler
from jmstvcamp.utils import string2filename
from jmstvcamp.framework.decorators import html, logged_in

class NameSchema(formencode.Schema):
    name = formencode.All(formencode.validators.UnicodeString(not_empty=True) )
#formencode.validators.PlainText())

class IndexHandler(Handler):
    """show the doku page"""

    template="doku.html"

    def get(self, errors={}, values={}):
        orig_pads = self.settings.db.pads.find().sort("date",-1)
        pads = []
        uid = self.userid
        for pad in orig_pads:
            pad['mine'] = pad['user']==self.userid
            pads.append(pad)
        
        return self.render(errors=errors, values = values, pads=pads)

    @logged_in()
    def post(self):
        try:
            values = NameSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.get(errors=e.error_dict, values=self.request.form)
        name=values['name']
        url = "http://openetherpad.org/"+string2filename(name)

        # check if it already exists
        pad = self.settings.db.pads.find_one({'url' : url})
        if pad is not None:
            return self.redirect(url)

        # add a new pad
        pad = {
            '_id' : unicode(uuid.uuid4()),
            'url' : url,
            'name' : name,
            'user' : self.user['_id'],
            'date' : datetime.datetime.now(),
        }

        self.settings.db.pads.save(pad)
        self.settings.log.info("created new pad %s" %url)
        return self.redirect(url)
