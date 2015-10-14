from .menu import process_item, clear_menu_cache
from . import db


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


def get_partial_menu(vendor_id, cat_group):
    """
    Instead of retrieving the full menu, we retrieve a partial menu containing all the items we
    need based on the order's category group
    :param vendor_id:
    :param cat_group: the category group built with create_cat_group()
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


def accept_order(order_post):
    """
    vendor_id checking to be done higher up
    :param order_post:
    :return:
    """
    menu = get_partial_menu(order_post['vendor_id'], create_cat_group(order_post['order']))
    price = 0
    order = order_post['order']
    pretty_order = order_post['pretty'] = []

    for record in order:
        menu_item = menu[record['category']]["items"][record['item']]
        p = {'name': menu_item['name']}
        subtotal = 0

        if 'size' in record:
            sz = menu_item['size'][record['size']]
            p['size'] = sz['name']
            subtotal += sz['price']
        else:
            subtotal += menu_item['price']

        if 'custom' in record:
            p['custom'] = []
            for i, cat in enumerate(record['custom']):
                customization = menu_item['custom'][i]
                res = []
                if customization['max'] > 0:
                    cat = cat[:customization['max']]
                for j in cat:
                    res.append(customization['options'][j]['name'])

                s_lim = customization['soft']
                if len(cat) > s_lim > 0:
                    for j in cat[s_lim:]:
                        subtotal += customization['options'][j]['price']

                if len(res) > 0:
                    p['custom'].append({
                        "name": customization.get("name", "untitled"),
                        "selection": res
                    })
        qty = record.get('qty', record.get('quantity', 1))
        p['quantity'] = qty
        p['price'] = subtotal
        subtotal *= qty
        p['sub_total'] = subtotal
        pretty_order.append(p)
        price += subtotal

    order_post['grand_total'] = price
    return order_post


sample_order_post = {
    "email": "anish.george@jlabs.co",
    "phone": "9711154215",
    "vendor_id": 1,
    "order": [
        {
            "category": 2,
            "item": 0,
            "size": 2,
            "custom": [
                [1, 2], [5], []
            ],
            "qty": 2
        },
        {
            "category": 3,
            "item": 2,
            "qty": 3
        },
        {
            "category": 4,
            "item": 4,
            "qty": 1
        }
    ]
}

def testSample():
    from pprint import PrettyPrinter
    printer = PrettyPrinter(indent=2)
    printer.pprint(accept_order(sample_order_post))
