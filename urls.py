from django.conf.urls import url
from django.contrib import admin

from .views.drs import vis_drs, data_drs
from .views.report import report_list, report_view
from .views.actor import actor_list, actor_view
from .views.identity import identity_list, identity_view
from .tables import ReportData, ThreatActorData, IdentityData

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^report/$', report_list),
    url(r'^actor/$', actor_list),
    url(r'^identity/$', identity_list),
    url(r'^data/report/', ReportData.as_view(), name="report_data"),
    url(r'^data/actor/', ThreatActorData.as_view(), name="threatactor_data"),
    url(r'^data/identity/', IdentityData.as_view(), name="identity_data"),
    url(r'^report/(?P<id>\d+)$', report_view),
    url(r'^actor/(?P<id>\d+)$', actor_view),
    url(r'^threat-actor/(?P<id>\d+)$', actor_view),
    url(r'^identity/(?P<id>\d+)$', identity_view),
    url(r'^vis/drs/$', vis_drs),
    url(r'^data/drs/$', data_drs),
    url(r'^$', vis_drs),
]
