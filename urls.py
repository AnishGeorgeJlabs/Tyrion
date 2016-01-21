from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from . import api, security, merchant_api


@csrf_exempt
def test(request):
    if request.method == "GET":
        extra = {
            "method": "GET",
            "requestData": request.GET
        }
    else:
        extra = {
            "method": "POST",
            "requestData": request.body
        }
    return JsonResponse({
        "result": True,
        "Message": "Test api, ECHO",
        "extra": extra
    })

urlpatterns = [
    url(r'^$', test),

    # --------- Customer app urls --------- #
    url(r'^menu$', api.get_menu),
    url(r'^menu/check_version$', api.check_menu_version),
    url(r'order$', api.place_order),
    url(r'history$', api.history),
    url(r'feedback$', api.feedback),
    url(r'details$', api.details),
    url(r'address$', api.address),
    url(r'areas$', api.areas),
    url(r'user/login$', api.login),
    url(r'user/signup$', api.signup),

    # ---------- Merchant app urls -------- #
    url(r'^login$', security.login),
    url(r'^change_pass$', security.change_password),

    url(r'^order_list$', security.auth(merchant_api.get_order_list)),
    url(r'^order_data$', security.auth(merchant_api.get_complete_order)),
    url(r'^order_data/update_status$', security.auth(merchant_api.update_status))

]


