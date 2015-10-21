from django.views.decorators.csrf import csrf_exempt

from .data.menu import get_version, get_full_menu as data_menu
from . import basic_failure, basic_success, basic_error, get_json
from .data.order import accept_order


def get_menu(request):
    """
    Get the Menu for a given vendor
    :GET.param vendor_id: An integer id for the required vendor
    :returns JSON[data]:  { "menu": {...}, "version": <int>, "vendor_id": <int> }
    """
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        return basic_failure("No vendor id specified")
    vendor_details = data_menu(int(vendor_id))
    if not vendor_details:
        return basic_failure("Invalid vendor or bad data")
    else:
        return basic_success(vendor_details)

def check_menu_version(request):
    """
    Short request to check the menu version. Used by app to check against the server whether it has the latest menu
    version with it or not
    :GET.param vendor_id: The integer vendor id
    :GET.param version or v: An integer specifying the version in place with the mobile app
    :returns JSON[data]: True if the version is current, else False
    """
    vendor_id = request.GET.get('vendor_id')
    version = request.GET.get('v', request.GET.get('version'))
    if not vendor_id or not version:
        return basic_failure("Parameters missing, Please specify a vendor_id and a version")
    db_version = get_version(int(vendor_id))
    if not db_version:
        return basic_failure("Invalid vendor or bad data")
    else:
        return basic_success(version == db_version)


@csrf_exempt
def place_order(request):
    try:
        order_post = get_json(request)

        for key in ['vendor_id', 'name', 'email', 'phone', 'area']:
            if key not in order_post or str(order_post[key]) == '':
                return basic_failure("Invalid "+key)

        res = accept_order(order_post)
        return basic_success(res)

    except Exception as e:
        return basic_error(e)
