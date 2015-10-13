"""
This package exposes methods to get the menu from database, following all the given relations
"""
from . import db
from .cache import Cache

_cache = Cache('menu')


def get_version(vendor_id):
    vendor = db.menu.find_one({"vendor_id": vendor_id}, {"version": True, "_id": False})
    if not vendor:
        return None
    else:
        return vendor.get("version")


def get_menu(vendor_id):
    _cache.clear()

    vendor = db.menu.find_one({"vendor_id": vendor_id}, {"_id": False})
    if 'menu' not in vendor:
        return None

    for category in vendor['menu']:
        for item in category['items']:
            ts_fk = item.pop('template_size_fk', None)
            tc_fk = item.pop('template_customize_fk', None)
            if ts_fk:
                key = 'template_size:' + str(ts_fk)
                cached = _cache.retrieve(key)
                if cached:
                    item['size'] = cached
                else:
                    item['size'] = get_template_size(ts_fk, vendor_id)
                    _cache.store('template_size:' + str(ts_fk), item['size'])

                item['simple'] = False
            else:
                if 'price' not in item:
                    item['price'] = 0
                    item['error'] = "Price not found"
                item['simple'] = True
            if tc_fk:
                key = 'template_customize:' + str(tc_fk)
                cached = _cache.retrieve(key)
                if cached:
                    item['custom'] = cached
                else:
                    item['custom'] = get_template_customize(tc_fk, vendor_id)
                    _cache.store(key, item['custom'])

    return vendor


def process_customization(cust_obj, vendor_id):
    customize_fk = cust_obj.pop('customize_fk', None)
    if customize_fk:
        key = 'customization:' + str(customize_fk)
        cached = _cache.retrieve(key)
        if cached:
            customization = cached
        else:
            customization = db.customize.find_one(
                {"customize_id": customize_fk, "vendor_id": vendor_id},
                {"_id": False, "vendor_id": False, "customize_id": False}
            )
            _cache.store(key, customization)
        cust_obj.update(customization)
    return cust_obj


def get_template_customize(template_fk, vendor_id):
    template = db.template_customize.find_one(
        {"template_id": template_fk, "vendor_id": vendor_id},
        {"_id": False, "custom": True}
    )
    if not template:
        print("No template found")
        return None
    elif not template.get('custom'):
        print("Empty template!!")
        return None
    else:
        custom = template['custom']
        for section in custom:
            process_customization(section, vendor_id)
        return custom


def get_template_size(template_fk, vendor_id):
    template = db.template_size.find_one(
        {"template_id": template_fk, "vendor_id": vendor_id},
        {"_id": False, "size": True}
    )
    if not template:
        return None
    return template.get('size')
