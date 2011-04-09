import index
import neu
import vote

def setup_handlers(map):
    with map.submapper(path_prefix="/themen") as m:
        m.connect(None, '', handler=index.IndexHandler)
        m.connect(None, '/', handler=index.IndexHandler)
        m.connect(None, '/new', handler=neu.NewHandler)
        m.connect(None, '/{tid}/vote', handler=vote.VoteHandler)
