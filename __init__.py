__author__ = 'jlabs-11'
__package__ = 'tyrion'

import pymongo
from django.http import HttpResponse
from bson.json_util import dumps, loads

# ------- Database Authentication and access ---------------- #
import json
import os

file = os.path.join(
    os.path.dirname(__file__),
    'db_creds.json'
)
with open(file, 'r') as cfile:
    creds = json.load(cfile)['tyrion']

dbclient = pymongo.MongoClient("45.55.232.5:27017")
dbclient.cersei.authenticate(creds['u'], creds['p'], mechanism='MONGODB-CR')

db = dbclient.tyrion

def get_json(request):
    return loads(request.body.decode())

# ------- Json response format ------------------------------ #
def jsonResponse(d):
    return HttpResponse(dumps(d), content_type='application/json')

def basic_failure(reason=None):
    return base_response(success=False, ekey="reason", reason=reason)

def basic_error(reason=None):
    return base_response(success=False, ekey="error", reason=str(reason))

def basic_success(data=None):
    return base_response(success=True, data=data)

def base_response(success=False, data=None, ekey="reason", reason=None):
    res = {"success": success}

    if data is not None:
        res['data'] = data

    if reason is not None:
        res[ekey] = reason
    return jsonResponse(res)

# -------------------------------------------------------------- #
import json
import os
