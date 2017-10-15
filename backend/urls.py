from django.conf.urls import url, include
from backend.roadtrip import views
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^questions/$', views.roadtrip_list),
]