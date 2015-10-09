__author__ = 'jlabs-11'
__package__ = 'tyrion'

import pymongo
from django.http import HttpResponse
from bson.json_util import dumps

dbclient = pymongo.MongoClient("45.55.232.5:27017")
dbclient.tyrion.authenticate("tyrionApi", "halfman", mechanism='MONGODB-CR')

db = dbclient.tyrion

def jsonResponse(d):
    return HttpResponse(dumps(d), content_type='application/json')

def basic_failure(reason=None):
    res = {"success": False}
    if reason:
        res['reason'] = reason

    return jsonResponse(res)

def basic_error(reason=None):
    res = {"success": False}
    if reason:
        res['error'] = reason

    return jsonResponse(res)

def basic_success(data=None):
    res = {"success": True}
    if data:
        res['data'] = data
    return jsonResponse(res)
