from django.views.decorators.csrf import csrf_exempt

from . import db, get_json, basic_failure, basic_error, basic_success

@csrf_exempt
def login(request):
    data = get_json(request)
    for key in ['username', 'password']:
        if key not in data:
            return basic_error(key+" missing")

    res = db.credentials.find_one({"username": data['username'], "password": data['password']})
    if res:
        return basic_success({
            "vendor_id": int(res['vendor_id']),
            "api_key": str(res['_id'])
        })
    else:
        return basic_failure("Unauthorized access")
