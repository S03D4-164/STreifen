from django.shortcuts import render

from ..models import *
from ..forms import *

def report_list(request):
    form = CreateReportForm()
    if request.method == "POST":
        form = CreateReportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            labels = form.cleaned_data["labels"]
            r = Report.objects.create(
                name = name,
                description = description,
            )
            r.save()
            if r and labels:
                r.labels=labels
                r.save()
    report = Report.objects.all()
    if report:
        report = report[0]
        print(report)
    c = {
        "form": form,
        "report": report,
    }
    return render(request, 'report_list.html', c)

def report_view(request, id):
    report = Report.objects.get(id=id)
    form = CreateReportForm(instance=report)
    if request.method == "POST":
        form = CreateReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
    c = {
        "form": form,
        "report": report,
    }
    return render(request, 'report_view.html', c)
