import register
import validate
import code
import profile

def setup_handlers(map):
    with map.submapper(path_prefix="/user") as m:
        m.connect(None, '/register', handler=register.Register)
        m.connect(None, '/validate', handler=validate.Validate)
        m.connect(None, '/newcode', handler=code.NewCode)
        m.connect(None, '/newpw', handler=code.NewPassword)
        m.connect(None, '/profile', handler=profile.Profile)
        m.connect(None, '/{username}/profile', handler=profile.Profile)
        m.connect(None, '/edit', handler=profile.Edit)

