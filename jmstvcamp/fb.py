import base64
import hashlib
import hmac
import json
import urllib2

def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "="*padding_factor 
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

def parse_signed_request(signed_request, secret):

    l = signed_request.split('.', 2)
    encoded_sig = l[0]
    payload = l[1]

    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        #log.error('Unknown algorithm')
        return None
    else:
        expected_sig = hmac.new(secret, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
        return None
    else:
        #log.debug('valid signed request received..')
        return data

def retrieve_email(signed_request, secret):
    data = parse_signed_request(signed_request, secret)
    if data is None:
        return None
    userid = data['user_id']
    token = data['oauth_token']
    url = "https://graph.facebook.com/%s?fields=id,email,first_name,last_name,gender,name&access_token=%s" %(userid, token)
    r = urllib2.urlopen(url)
    payload = r.read()
    userdata = json.loads(payload)
    return userdata

