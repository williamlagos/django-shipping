from django.conf.urls import patterns,url,include
from demo.views import *

urlpatterns = [
    url(r'^$',main),
    url(r'^shipping/',include('shipping.urls')),
    url(r'^spreadapp',init_spread),
    url(r'^products',store_main),
    url(r'^cancel',cancel),
    url(r'^delivery',delivery),
    url(r'^correios',mail),
    url(r'^spreadable',spreadable),
    url(r'^spreaded',spreaded),
    url(r'^spreadspread',spreadspread),
    url(r'^spread',main),
    url(r'^playable',playable),
    url(r'^images',image),
    url(r'^image',imageview),
    url(r'^contents',content),
    url(r'^expose',upload),
    url(r'^media',media),
    url(r'^productimage',product_image)
]
