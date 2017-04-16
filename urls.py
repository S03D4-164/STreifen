from django.conf.urls import url
from django.contrib import admin

from .views.visualize import vis_drs
from .views.report import report_list, report_view
from .tables import ReportData

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^data/report/', ReportData.as_view(), name="report_data"),
    url(r'^report/$', report_list),
    url(r'^report/(?P<id>\d+)$', report_view),
    #url(r'^vis/drs', vis_drs),
    url(r'^$', vis_drs),
]
