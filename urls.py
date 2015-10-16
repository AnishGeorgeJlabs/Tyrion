from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from . import api, security


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
    url(r'^login$', security.login),
    url(r'^menu$', api.get_menu),
    url(r'^menu/check_version$', api.check_menu_version),

    url(r'order', api.place_order)
]


