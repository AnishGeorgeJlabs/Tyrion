from .data.menu import get_version, get_menu as data_menu
from . import basic_failure, basic_success

def get_menu(request):
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        return basic_failure("No vendor id specified")
    vendor_details = data_menu(int(vendor_id))
    if not vendor_details:
        return basic_failure("Invalid vendor or bad data")
    else:
        return basic_success(vendor_details)

def check_menu_version(request):
    vendor_id = request.GET.get('vendor_id')
    version = request.GET.get('v', request.GET.get('version'))
    if not vendor_id or not version:
        return basic_failure("Parameters missing, Please specify a vendor_id and a version")
    db_version = get_version(int(vendor_id))
    if not db_version:
        return basic_failure("Invalid vendor or bad data")
    else:
        return basic_success(version == db_version)


