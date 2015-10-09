from .data.menu import process_customization, get_template_customize, get_template_size, get_menu
import pprint

printer = pprint.PrettyPrinter(indent=2)

def test1():
    arr = [{"customize_fk": 3}, {"customize_fk": 4, "soft_limit": 3}]
    a2 = [process_customization(x, 1) for x in arr]
    print("arr: "+str(arr))
    print("a2: "+str(a2))

def test2():
    template = get_template_size(6, 1)
    printer.pprint(template)

def test3():
    vendor = get_menu(1)
    printer.pprint(vendor)
