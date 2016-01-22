from django.views.decorators.csrf import csrf_exempt

from .data.menu import get_version, get_full_menu as data_menu
from . import basic_failure, basic_success, basic_error, get_json
from .data.order import accept_order
from . import db


def get_menu(request):
    """
    Get the Menu for a given vendor
    :GET.param vendor_id: An integer id for the required vendor
    :returns JSON[data]:  { "menu": {...}, "version": <int>, "vendor_id": <int> }
    """
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        return basic_failure("No vendor id specified")
    vendor_details = data_menu(int(vendor_id))
    if not vendor_details:
        return basic_failure("Invalid vendor or bad data")
    else:
        return basic_success(vendor_details)


def check_menu_version(request):
    """
    Short request to check the menu version. Used by app to check against the server whether it has the latest menu
    version with it or not
    :GET.param vendor_id: The integer vendor id
    :GET.param version or v: An integer specifying the version in place with the mobile app
    :returns JSON[data]: True if the version is current, else False
    """
    vendor_id = request.GET.get('vendor_id')
    version = request.GET.get('v', request.GET.get('version'))
    if not vendor_id or not version:
        return basic_failure("Parameters missing, Please specify a vendor_id and a version")
    db_version = get_version(int(vendor_id))
    if not db_version:
        return basic_failure("Invalid vendor or bad data")
    else:
        return basic_success(int(version) == db_version)


@csrf_exempt
def place_order(request):
    try:
        order_post = get_json(request)

        for key in ['vendor_id', 'name', 'email', 'phone', 'area']:
            if key not in order_post or str(order_post[key]) == '':
                return basic_failure("Invalid " + str(key))

        res = accept_order(order_post)
        return basic_success(res)

    except Exception as e:
      raise


def details(request):
    vendor_id = int(request.GET['vendor_id'])
    order_number = request.GET['order_number']
    order = db.orders.find_one({"vendor_id": vendor_id, "order_number": order_number},
                               {"_id": 0, "pretty_order": 1, "amount": 1, "status": 1, "order_number": 1})
    if not order:
        return basic_failure("Cannot find order")
    order['status'] = order['status'][0]['status']
    order['order'] = order.pop('pretty_order')
    amount = order.pop('amount')
    amount.pop('net_untaxable')
    amount.pop('net_after_tax')
    amount.pop('net_taxable')
    order.update(amount)
    return basic_success(order)


def process_order(order):
    # correct the orders
    for item in order['order']:
        if 'custom' in item:
            custom = item.pop('custom')
            new_cust = []
            for option in custom:
                for sel in option['selection']:
                    new_cust.append(sel['name'])
            item['custom'] = new_cust


def history(request):
    try:
        email = request.GET["email"]
        vendor_id = int(request.GET['vendor_id'])
        status_list = request.GET.get('status', 'placed,accepted,cancelled,ready,delayed,delivered').split(',')
        orders = list(db.orders.aggregate([
            {"$match": {"email": email, "vendor_id": vendor_id, "status.0.status": {
                "$in": status_list
            }}},
            {"$sort": {"timestamp": -1}},
            {"$project": {
                "_id": 0,
                "order_number": 1,
                "status": "$status.status",
                "delivery_charge": "$amount.delivery_charges",
                "tax": "$amount.tax",
                "total": "$amount.net_amount_payable",
                "order": "$pretty_order"
            }}
        ]))

        for order in orders:
            # Correct status
            order['status'] = order['status'][0]
            process_order(order)
        return basic_success(orders)
    except Exception as e:
        return basic_error(e)


@csrf_exempt
def feedback(request):
    try:
        data = get_json(request)
        email = data['email']
        phone = data['phone']
        vendor_id = data['vendor_id']
        subject = data.get('subject', 'Feedback')
        body = data['body']
        # Todo, do something with this data
        return basic_success(True)
    except Exception as e:
        return basic_error(e)


@csrf_exempt
def address(request):
    try:
        if request.method == "GET":
            email = request.GET["email"]
            vendor_id = int(request.GET['vendor_id'])
            user = db.users.find_one(
                {"email": email, "vendor_id": vendor_id},
                {"_id": 0, "addresses": 1}
            )
            if not user:
                return basic_failure("User not found")
            else:
                return basic_success(user.get("addresses", []))
        elif request.method == "POST":
            data = get_json(request)
            email = data['email']
            vendor_id = int(data['vendor_id'])
            address = data['address']
            db.users.update_one(
                {"email": email, "vendor_id": vendor_id},
                {"$push": {"addresses": address}},
                upsert=True
            )
            return basic_success()
        else:
            return basic_error("Unsupported method")
    except Exception as e:
        return basic_error(e)

def areas(request):
    try:
        if request.method != "GET":
            return basic_failure("Unsupported method")
        else:
            vendor_id = int(request.GET['vendor_id'])
            areas = list(db.delivery_charges.find(
                {"charges.vendor_id": vendor_id},
                {"area": 1, "_id": 0}
            ))
            return basic_success([x.get("area") for x in areas])
    except Exception as e:
        return basic_error(e)


@csrf_exempt
def login(request):
    try:
        if request.method != "POST":
            return basic_failure("Unsupported mothod")
        else:
            data = get_json(request)
            return basic_success(db.users.count({
                "email": data['email'],
                "vendor_id": data['vendor_id'],
                "password": data['password']
            }) != 0)
    except Exception as e:
        return basic_error(e)

@csrf_exempt
def signup(request):
    try:
        if request.method != "POST":
            return basic_failure("Unsupported mothod")
        else:
            data = get_json(request)
            user = {
                "email": data['email'],
                "vendor_id": data['vendor_id'],
                }
            if db.users.count(user) != 0:
                return basic_failure("User already exists")
            else:
                user["password"] = data['password']
                res = db.users.insert_one(user)
                return basic_success(bool(res.inserted_id))
    except Exception as e:
        return basic_error(e)
    

