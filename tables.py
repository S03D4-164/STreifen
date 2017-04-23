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
            return '<a onclick=ChangeRight({0}) class="btn btn-primary btn-xs">{0}</button>'.format(row.id)
        elif column == 'name':
            return '<a href="/report/{0}">{1}</a>'.format(row.id,row.name)
        else:
            return super(ReportData, self).render_column(row, column)
