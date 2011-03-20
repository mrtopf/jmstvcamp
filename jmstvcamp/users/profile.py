# encoding=latin1
import formencode
import werkzeug
from jmstvcamp.framework import Handler
from jmstvcamp.framework.decorators import html, logged_in

class Profile(Handler):
    """show a user profile"""

    template="profile.html"

    def get(self, username=None):
        """display a user profile"""
        ownprofile = False
        if username is None:
            # try to use the logged in user if existing
            user = self.user
            print user
            if user is None:
                raise werkzeug.exceptions.NotFound()
        else:
            user = self.settings.users.get_by_id(username)
            if user is None:
                raise werkzeug.exceptions.NotFound()
       
        if self.user is not None:
            ownprofile = self.user['_id'] == user['_id']

        return self.render(ownprofile = ownprofile)

class ProfileSchema(formencode.Schema):
    name = formencode.All(formencode.validators.UnicodeString(not_empty=True))
    attend = formencode.validators.OneOf(['yes','no','maybe'])
    organization = formencode.All(formencode.validators.UnicodeString())
    homepage = formencode.validators.URL()
    bio = formencode.validators.UnicodeString()
    twitter = formencode.validators.UnicodeString()

class Edit(Handler):
    """show the profile edit page for logged in users"""

    template="editform.html"

    @logged_in()
    def get(self):
        return self.render(errors={}, values=self.user)

    @logged_in()
    def post(self):
        """update profile"""
        print self.request.form
        try:
            values = ProfileSchema.to_python(self.request.form)
        except formencode.validators.Invalid, e:
            return self.render(errors=e.error_dict, values=self.request.form)

        user = self.settings.users.save(self.user, values) 
        # TODO: Add flash message
        return self.redirect("/user/profile")


