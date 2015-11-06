from django.views.decorators.csrf import csrf_exempt

from bson.json_util import ObjectId
from . import db, get_json, basic_failure, basic_error, basic_success

@csrf_exempt
def login(request):
    data = get_json(request)
    for key in ['username', 'password']:
        if key not in data:
            return basic_error(key+" missing")

    res = db.credentials.find_one({"username": data['username'], "password": data['password']})
    if res:
        vendor_id = int(res['vendor_id'])
        mer = db.merchants.find_one({"vendors.vendor_id": vendor_id}, {"vendors.$": True, "name": True})
        return basic_success({
            "vendor_id": vendor_id,
            "api_key": str(res['_id']),
            "name": mer['name'],
            "address": mer['vendors'][0]['address']
        })
    else:
        return basic_failure("Unauthorized access")

@csrf_exempt
def change_password(request):
    opts = get_json(request)
    for key in ['api_key', 'vendor_id', 'old_pass', 'new_pass', 'username']:
        if key not in opts:
            return basic_error(key+" missing, unauthorized access")
    update = db.credentials.update_one({
        "_id": ObjectId(opts['api_key']),
        "username": opts['username'],
        "password": opts['old_pass'],
        "vendor_id": opts['vendor_id']
    }, {"$set": {"password": opts['new_pass']}})
    return basic_success(update.modified_count == 1)

def auth(handler):
    """ Authorization layer for merchant application
    :param handler: A function which will take 2 parameters (options, vendor_id) and return JSON response
    :return: the handler function wrapped with the authorization middleware
    """
    @csrf_exempt
    def authorized_access(request):
        if request.method == "GET":
            opts = request.GET.copy()
        else:
            opts = get_json(request)

        for key in ['api_key', 'vendor_id']:
            if key not in opts:
                return basic_error(key+" missing, unauthorized access")

        api_key = opts.get('api_key')
        vendor_id = int(opts.get('vendor_id'))
        try:
            if db.credentials.count({"_id": ObjectId(api_key), "vendor_id": vendor_id}) > 0:
                return handler(opts, vendor_id, request.method)
            else:
                return basic_failure("Unauthorized access")
        except Exception as e:
            return basic_error("Handler error: "+str(e))

    return authorized_access
