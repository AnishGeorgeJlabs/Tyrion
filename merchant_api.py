from datetime import datetime

from . import db, basic_success, basic_failure


def get_order_list(opts, vendor_id, method):
    status = opts.get('status', 'placed')
    res = list(db.orders.aggregate([
        {"$match": {"vendor_id": vendor_id, "status.0.status": status}},
        {"$unwind": "$status"},
        {"$match": {"status.status": status}},
        {"$project": {
            "order_number": 1,
            "status": "$status.status",
            "area": 1,
            "total": "$amount.net_amount_payable",
            "_id": 0
        }},
    ]))
    return basic_success(res)


def get_complete_order(opts, vendor_id, method):
    order_number = opts['order_number']
    order = db.orders.find_one({"order_number": order_number}, {"_id": False, "order": False})
    if order is None:
        return basic_failure("Invalid order number")
    else:
        order['status'] = order['status'][0]['status']
        order['timestamp'] = order['timestamp']
        return basic_success(order)


def update_status(opts, vendor_id, method):
    if method != 'POST':
        return basic_failure("GET not authorized")
    order_number = opts['order_number']
    status = opts['status']
    res = db.orders.update_one({'order_number': order_number},
                               {"$push": {"status": {
                                   "$each": [{"status": status, "time": datetime.now()}],
                                   "$position": 0
                               }}})
    return basic_success((res.modified_count > 0))
