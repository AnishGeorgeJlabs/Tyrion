from .menu import process_item, clear_menu_cache
from . import db


def create_cat_group(order):
    cat_group = {}
    for item in order:
        cat = item['category']
        if cat in cat_group:
            cat_group[cat].append(item['item'])
        else:
            cat_group[cat] = [item['item']]
    return cat_group


def get_partial_menu(vendor_id, cat_group):
    clear_menu_cache()

    vendor = db.menu.find_one({"vendor_id": vendor_id}, {"_id": False})
    if 'menu' not in vendor:
        return None

    cats = cat_group.keys()

    for i, category in enumerate(vendor['menu']):
        if i in cats:
            for j, item in enumerate(category['items']):
                if j in cat_group[i]:
                    process_item(item, vendor_id)
    return vendor['menu']
