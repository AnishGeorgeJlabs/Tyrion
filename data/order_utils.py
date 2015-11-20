from .cache import Cache
from .. import db
from datetime import datetime, date, time

# Sample order number: BAK0050515-001

prefix_cache = Cache('vendor_prefix')
delivery_cache = Cache('delivery_charges')
vendor_cache = Cache('vendor_names')


def get_vendor_prefix(vendor_id):
    """ Get the prefix used for order number
    :param vendor_id: usual
    :return:
    """
    prefix = prefix_cache.retrieve(vendor_id)
    if prefix is None:
        merchant = db.merchants.find_one({"vendors.vendor_id": vendor_id}, {"prefix": True, "vendors": True})
        prefix = merchant.get('prefix', 'UNK')
        for i, v in enumerate(merchant['vendors']):
            if v['vendor_id'] == vendor_id:
                prefix += str(i)
                break
        prefix_cache.store(vendor_id, prefix)
    return prefix


def generate_order_number(vendor_id):
    """ Generates a unique order number and returns that along with the timestamp
    :param vendor_id:
    :return:
    """
    now = datetime.now()
    today = datetime.combine(date.today(), time(0))
    num = db.orders.count({"vendor_id": vendor_id, "timestamp": {"$gte": today}}) + 1
    prefix = get_vendor_prefix(vendor_id)

    order_num = prefix + now.strftime("%d%m%y") + "-{0:03d}".format(num)

    return order_num, now

def get_delivery_charges(area, vendor_id):
    key = str(vendor_id) + ":" + area
    charges = delivery_cache.retrieve(key)
    if not charges:
        d = db.delivery_charges.find_one({"area": area, "charges.vendor_id": vendor_id}, {"charges.$": True})
        if not d:
            delivery_cache.store(key, 0)
            return 0
        else:
            res = d['charges'][0].get('charge', 0)
            delivery_cache.store(key, res)
            return res

def get_vendor(vendor_id):
    vendor = vendor_cache.retrieve(str(vendor_id))
    if not vendor:
        merchant = db.merchants.find_one({"vendors.vendor_id": vendor_id}, {"vendors.$": True, "name": True})
        vendor = {
            "name": merchant['name'],
            "address": merchant['vendors'][0]['address']
        }
        vendor_cache.store(str(vendor_id), vendor)
    return vendor

