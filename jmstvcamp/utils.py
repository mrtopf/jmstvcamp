import markdown
import re
import string
import os.path
from unicodedata import decomposition, normalize

md = markdown.Markdown(safe_mode="remove")
lre_string = re.compile(r'(?P<protocal>(^|\s)((http|ftp)://.*?))(\s|$)', re.S|re.M|re.I)

def linkify(text):
    def do_sub(m):
        c = m.groupdict()
        if c['protocal']:
            url = m.group('protocal')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br>'
            return '%s<a href="%s">%s</a>%s' % (prefix, url, url, last)
    return re.sub(lre_string, do_sub, text)

def markdownify(text):
    return linkify(md.convert(text))



mapping = {
    196 : 'AE', 198 : 'AE', 214 : 'OE', 220 : 'UE', 223 : 'ss', 224 : 'a',
    228 : 'ae', 230 : 'ae', 246 : 'oe', 252 : 'ue'
}

def string2filename(s):
    """convert a string to a valid filename"""
    

    s = s.strip()
    s = s.lower()

    # remove an eventual path
    s = s.replace("\\","/")
    _, s = os.path.split(s)
    
    res = u''
    mkeys = mapping.keys()
    for c in s:
        o = ord(c)
        if o in mapping.keys():
            res = res+mapping[o]
            continue
        if decomposition(c):
            res = res + normalize('NFKD', c)
        else:
            res = res + c
    
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    res = ''.join(c for c in res if c in valid_chars)
    res = res.replace(" ","-")
    return res


