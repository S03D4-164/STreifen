from django.shortcuts import render, redirect

import STreifen.models as mymodels
import STreifen.forms as myforms
from ..models import *
from ..forms import *
import stix2

def stix_report(rep):
    objects = ()
    for ref in rep.object_refs.all():
        obj = myforms.get_obj_from_id(ref)
        if obj.object_type.name == 'identity':
            i = stix2.Identity(
                id=obj.object_id.object_id,
                name=obj.name,
                identity_class=obj.identity_class,
                description=obj.description,
                sectors=[str(s.value) for s in obj.sectors.all()],
            )
            objects += (i,)
        elif obj.object_type.name == 'attack-pattern':
            a = stix2.AttackPattern(
                id=obj.object_id.object_id,
                name=obj.name,
                description=obj.description,
            )
            objects += (a,)
        elif obj.object_type.name == 'malware':
            m = stix2.Malware(
                id=obj.object_id.object_id,
                name=obj.name,
                description=obj.description,
                labels=[str(l.value) for l in obj.labels.all()],
            )
            objects += (m,)
        elif obj.object_type.name == 'threat-actor':
            t = stix2.ThreatActor(
                id=obj.object_id.object_id,
                name=obj.name,
                description=obj.description,
                labels=[str(l.value) for l in obj.labels.all()],
                aliases=[str(a.name) for a in obj.aliases.all()],
            )
            objects += (t,)
        elif obj.object_type.name == 'relationship':
            r = stix2.Relationship(
                id=obj.object_id.object_id,
                relationship_type=obj.relationship_type.name,
                description=obj.description,
                source_ref=obj.source_ref.object_id,
                target_ref=obj.target_ref.object_id,
            )
            objects += (r,)
        elif obj.object_type.name == 'sighting':
            s = stix2.Sighting(
                id=obj.object_id.object_id,
                sighting_of_ref=obj.sighting_of_ref.object_id,
                where_sighted_refs=[str(w.object_id) for w in obj.where_sighted_refs.all()],
                first_seen=obj.first_seen,
                last_seen=obj.last_seen,
            )
            objects += (s,)
    report = stix2.Report(
        id=rep.object_id.object_id,
        labels=[str(l.value) for l in rep.labels.all()],
        name=rep.name,
        description=rep.description,
        published=rep.published,
        object_refs=[str(r.object_id) for r in rep.object_refs.all()],
    )
    objects += (report,)
    bundle = stix2.Bundle(*objects)
    return bundle

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
    c = {
        "form": form,
    }
    return render(request, 'report_list.html', c)

def _object_form(name, request=None, report=None):
    post = None
    if request:
        if request.method == 'POST':
            post = request.POST
    if name == "identity":
        return CreateIdentityForm(post)
    elif name == "attack-pattern":
        return CreateAttackPatternForm(post)
    elif name == "malware":
        return CreateMalwareForm(post)
    elif name == "threat-actor":
        return CreateThreatActorForm(post)
    elif name == "relationship":
        form = CreateRelationshipForm(post)
        if report:
            choices = myforms.object_choices(
                ids=report.object_refs.all()
            )
            form.fields["source_ref"].choices = choices
            form.fields["target_ref"].choices = choices
        return form
    elif name == "sighting":
        form = CreateSightingForm(post)
        if report:
            wsr = myforms.object_choices(
                ids=report.object_refs.filter(
                    object_id__startswith="identity"
                )
            )
            form.fields["where_sighted_refs"].choices = wsr
            sor = myforms.object_choices(
                ids=report.object_refs.all().exclude(
                    object_id__startswith="relationship"
                ).exclude(
                    object_id__startswith="sighting"
                )
            )
            form.fields["sighting_of_ref"].choices = sor
        return form
    return False

def report_view(request, id):
    report = Report.objects.get(id=id)
    stix = stix_report(report)
    #print(stix)
    form = CreateReportForm(instance=report)
    soform = SelectObjectForm()
    selected = None
    coform = None
    aoform = AddObjectForm()
    if request.method == "POST":
        #print(request.POST)
        if 'update' in request.POST:
            form = CreateReportForm(request.POST, instance=report)
            if form.is_valid():
                form.save()
                redirect("/report/"+id)
        elif 'select' in request.POST:
            sotid = request.POST.get('select')
            sot = STIXObjectType.objects.get(id=sotid)
            selected = sot.name
            soform.fields["type"].initial = sotid
            coform = _object_form(selected, report=report)
        elif 'create_obj' in request.POST:
            sotid = request.POST.get('type')
            sot = STIXObjectType.objects.get(id=sotid)
            selected = sot.name
            soform.fields["type"].initial = sotid
            coform = _object_form(sot.name, request=request)
            if coform.is_valid():
                saved = coform.save()
                report.object_refs.add(saved.object_id)
                report.save()
                redirect("/report/"+id)
        elif 'add_obj' in request.POST:
            aoform = AddObjectForm(request.POST)
            if aoform.is_valid():
                objs = aoform.cleaned_data["objects"]
                for obj in objs:
                    report.object_refs.add(obj)
                report.save()
                redirect("/report/"+id)

    objects = []
    for ref in report.object_refs.all():
        objects.append(myforms.get_obj_from_id(ref))
    form.fields["object_refs"].choices = myforms.object_choices(
        report.object_refs.all()
    )
    c = {
        "form": form,
        "soform": soform,
        "selected": selected,
        "coform": coform,
        "aoform": aoform,
        "report": report,
        "objects": objects,
        "stix":stix,
    }
    return render(request, 'report_view.html', c)
