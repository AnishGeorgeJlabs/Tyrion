"""
This package exposes methods to get the menu from database, following all the given relations
"""
from . import db


def process_customization(cust_obj, vendor_id):
    customize_fk = cust_obj.pop('customize_fk')
    customization = db.customize.find_one(
        {"customize_id": customize_fk, "vendor_id": vendor_id},
        {"_id": False, "vendor_id": False, "customize_id": False}
    )
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

def get_menu(vendor_id):
    vendor = db.menu.find_one({"vendor_id": vendor_id}, {"_id": False})
    if 'menu' not in vendor:
        return None

    for category in vendor['menu']:
        for item in category['items']:
            ts_fk = item.pop('template_size_fk')
            tc_fk = item.pop('template_customize_fk')
            if ts_fk:
                item['size'] = get_template_size(ts_fk, vendor_id)
                item['simple'] = False
            else:
                if 'price' not in item:
                    item['price'] = 0
                    item['error'] = "Price not found"
                item['simple'] = True
            if tc_fk:
                item['custom'] = get_template_customize(tc_fk, vendor_id)

    return vendor
