from django_datatables_view.base_datatable_view import BaseDatatableView
from .models import *

class ReportData(BaseDatatableView):
    model = Report
    columns = ['id', 'created', 'name']
    order_columns = ['id', 'created', 'name']
    max_display_length = 100

    def get_initial_queryset(self):
        qs = Report.objects.all()
        return qs
    def render_column(self, row, column):
        if column == 'id':
            return '<a href="/report/{0}">{0}</a>'.format(row.id)
        else:
            return super(ReportData, self).render_column(row, column)
