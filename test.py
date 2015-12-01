# from .data.menu import process_customization, get_template_customize, get_template_size, get_full_menu
# import pprint
#
# printer = pprint.PrettyPrinter(indent=2)
#
# def test1():
#     arr = [{"customize_fk": 3}, {"customize_fk": 4, "soft_limit": 3}]
#     a2 = [process_customization(x, 1) for x in arr]
#     print("arr: "+str(arr))
#     print("a2: "+str(a2))
#
# def test2():
#     template = get_template_size(6, 1)
#     printer.pprint(template)

# def test3():
#     vendor = get_full_menu(1)
#     printer.pprint(vendor)

sample_orders = [
    {
        "email": "anish.george@jlabs.co",
        "name": "Anish George",
        "phone": "9711154215",
        "address": "163, typ-III, Av nagar",
        "area": "Ayurvigyan Nagar",
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
    },
    {
        "email": "jerrin.math@jlabs.co",
        "name": "Jerrin mathews",
        "phone": "9711154215",
        "address": "163, typ-III, Av nagar",
        "area": "Green Park",
        "vendor_id": 1,
        "order": [
            {
                "category": 2,
                "item": 0,
                "size": 2,
                "custom": [
                    [],  # Signature toppings
                    [5, 8],  # Gourmet toppings
                    []
                ]
            },
            {
                "category": 3,
                "item": 0,
                "custom": [[1, 2]]
            }
        ]
    },
    {
        "email": "anishgeorgeag@yahoo.in",
        "name": "Anish 'basso' George",
        "phone": "9871388191",
        "address": "153, Freedom fighter enclave",
        "area": "Green Park",
        "vendor_id": 2,
        "order": [
            {
                "category": 1,
                "item": 3,
                "qty": 2
            },
            {
                "category": 0,
                "subcat": 0,
                "item": 2
            },
            {
                "category": 0,
                "subcat": 1,
                "item": 10,
                "qty": 5
            }
        ]
    }
]

def test_api_orders(idx):
    import requests
    url = "http://127.0.0.1:8000/tyrion/order"
    r = requests.post(url, json=sample_orders[idx])
    print(r.json())
