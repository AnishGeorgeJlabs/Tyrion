"""
This package exposes methods to get the menu from database, following all the given relations
"""
from . import db
from .cache import Cache

_cache = Cache('menu')


def clear_menu_cache():
    _cache.clear()

def get_version(vendor_id):
    """ Checking menu version """
    vendor = db.menu.find_one({"vendor_id": vendor_id}, {"version": True, "_id": False})
    if not vendor:
        return None
    else:
        return vendor.get("version")


def get_full_menu(vendor_id):
    """ Main menu retrieval function
    We build the menu from a size template and a customization template
    1. Either the price or a size object will be present. in case of size object, it can be an embedded object
        or it may be a template reference
    2. The customization is optional, but if there, it will either be an object or a template reference """
    clear_menu_cache()
    vendor = db.menu.find_one({"vendor_id": vendor_id}, {"_id": False})
    if 'menu' not in vendor:
        return None

    for category in vendor['menu']:
        for item in category['items']:
            process_item(item, vendor_id)

    return vendor


def process_item(item, vendor_id):
    """ Process individual item, works on side effects
    :param item:
    :param vendor_id:
    :return:
    """
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


def process_customization(cust_obj, vendor_id):
    """ Lowest building block, process a given customization adding additional data from template
    :param cust_obj: The object having the customization reference inside the customization template
    :param vendor_id: as usual
    """
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
        # Now for some magic
        customization.update(cust_obj)

        # setup price
        if 'price' in customization:
            p = customization.pop('price')
            for option in customization['options']:
                option['price'] = p

        # Set up limits
        for key in ['min', 'max', 'soft']:
            if key not in customization:
                customization[key] = 0

        return customization
    else:
        return None


def get_template_customize(template_fk, vendor_id):
    """ Process the customization template, uses process_customization()
    Parses the template, adds any missing customizations
    :param template_fk: The foreign key for the template id in db.template_customize
    :param vendor_id: as usual
    """
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
        '''
        custom = template['custom']
        for section in custom:
            process_customization(section, vendor_id)
        '''
        custom = [process_customization(section, vendor_id) for section in template['custom']]
        return custom


def get_template_size(template_fk, vendor_id):
    """ Get the Size templates
    :param template_fk: Foreign key for size template in db.template_size
    :param vendor_id: as usual
    :return:
    """
    template = db.template_size.find_one(
        {"template_id": template_fk, "vendor_id": vendor_id},
        {"_id": False, "size": True}
    )
    if not template:
        return None
    return template.get('size')
