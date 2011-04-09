import index
import delete

def setup_handlers(map):
    with map.submapper(path_prefix="/doku") as m:
        m.connect(None, '', handler=index.IndexHandler)
        m.connect(None, '/', handler=index.IndexHandler)
        m.connect(None, '/{pid}/delete', handler=delete.DeleteHandler)
