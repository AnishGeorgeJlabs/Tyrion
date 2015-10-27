from .menu import process_item, clear_menu_cache
from . import db
from datetime import datetime
from .external_integration import place_order
from .order_utils import generate_order_number, get_delivery_charges


def create_cat_group(order):
    """
    Takes apart the order and creates a dictionary of category index mapped to list of item indices
    :param order: Just the actual order list
    :return: { <cat>: [<items>] }
    """
    cat_group = {}
    for item in order:
        cat = item['category']
        if cat in cat_group:
            cat_group[cat].append(item['item'])
        else:
            cat_group[cat] = [item['item']]
    return cat_group


def get_partial_menu(cat_group, vendor_id):
    """
    Instead of retrieving the full menu, we retrieve a partial menu containing all the items we
    need based on the order's category group
    :param cat_group: the category group built with create_cat_group()
    :param vendor_id:
    :return:
    """
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


def process_order(order, vendor_id):
    """
    vendor_id checking to be done higher up
    :param order: The order list
    :param vendor_id: usual
    :returns: (The pretty printed order list, grand total (as of now taxless))
    """
    menu = get_partial_menu(create_cat_group(order), vendor_id)
    total = 0
    untaxable = 0
    pretty_order = []

    for record in order:
        menu_item = menu[record['category']]["items"][record['item']]
        p = {'name': menu_item['name']}
        subtotal = 0

        # Getting the base price of the item
        if 'size' in record:
            sz = menu_item['size'][record['size']]
            p['size'] = sz['name']
            subtotal += sz['price']
            p['base_price'] = sz['price']
        else:
            subtotal += menu_item['price']
            p['base_price'] = menu_item['price']

        # Handling customization
        if 'custom' in record:
            p['custom'] = []
            for i, cat in enumerate(record['custom']):
                customization = menu_item['custom'][i]
                res = []
                if customization['max'] > 0:
                    cat = cat[:customization['max']]

                # for handling soft limits
                s_lim = customization['soft']

                for j, opt in enumerate(cat):
                    obj = {"name": customization['options'][opt]['name']}
                    if s_lim > 0 and j < s_lim:
                        obj['price'] = 0
                    else:
                        obj['price'] = customization['options'][opt]['price']
                        subtotal += obj['price']
                    res.append(obj)

                if len(res) > 0:
                    p['custom'].append({
                        "name": customization.get("name", "untitled"),
                        "selection": res
                    })
            p['price_after_customization'] = subtotal

        # Now multiply price with quantity
        qty = record.get('qty', record.get('quantity', 1))
        p['quantity'] = qty
        subtotal *= qty
        p['sub_total'] = subtotal

        pretty_order.append(p)  # add the item to the final order list

        if menu_item.get('taxable', False):
            untaxable += subtotal
        else:
            total += subtotal  # add up the current item's price to the grand total
        # End of for loop

    return pretty_order, total, untaxable


def accept_order(order_post):
    vendor_id = order_post['vendor_id']
    order = order_post['order']

    pretty, total, untaxable = process_order(order, vendor_id)

    tax_total = total * 1.125
    del_charges = get_delivery_charges(order_post['area'], vendor_id)
    gtotal = untaxable + tax_total + del_charges

    order_num, timestamp = generate_order_number(vendor_id)
    order_post.update({
        "pretty_order": pretty,
        "amount": {
            "net_taxable": total,
            "net_untaxable": untaxable,
            "net_after_tax": tax_total,
            "tax": tax_total - total,
            "delivery_charges": del_charges,
            "net_amount_payable": gtotal
        },
        "order_number": order_num,
        "timestamp": timestamp,
        "status": [
            {"status": "placed", "time": timestamp}
        ]
    })
    db.orders.insert_one(order_post)
    return gtotal
