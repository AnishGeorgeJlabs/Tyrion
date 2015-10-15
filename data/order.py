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


def accept_order(order, vendor_id):
    """
    vendor_id checking to be done higher up
    :param order: The order list
    :param vendor_id: usual
    :returns: (The pretty printed order list, grand total (as of now taxless))
    """
    menu = get_partial_menu(create_cat_group(order), vendor_id)
    price = 0
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

        price += subtotal  # add up the current item's price to the grand total
        # End of for loop

    return pretty_order, price


sample_order_post = {
    "email": "anish.george@jlabs.co",
    "name": "Anish George",
    "phone": "9711154215",
    "vendor_id": 1,
    "order": [
        {
            "category": 0,
            "item": 0,
            "size": 2,
            "custom": [
                [1],  # Crust
                [2],  # Sauce
                [1, 3, 15],  # Signature toppings
                [5, 8],  # Gourmet toppings
                []
            ]
        }
    ]
}
'''
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
'''


def testSample():
    from pprint import PrettyPrinter

    printer = PrettyPrinter(indent=2)
    a, b = accept_order(sample_order_post['order'], sample_order_post['vendor_id'])
    print("Order post")
    printer.pprint(sample_order_post)
    print("And the final result")
    printer.pprint(a)

    print("Grand total : " + str(b))
