import pymongo

coll = pymongo.Connection().jmstvcamp.users

for rec in coll.find():
    rec['queue_date'] = None
    rec['waitinglist'] = False
    if rec['state'] != "live":
        rec['queue_date'] = None
    elif rec['attend'] != "yes":
        rec['queue_date'] = None
    else:
        activation_date = None
        for r2 in rec['log']:
            if r2['msg']=="welcome mail sent":
                activation_date = r2['date']
        rec['queue_date'] = activation_date
    coll.save(rec)
