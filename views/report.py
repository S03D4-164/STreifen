from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

import STreifen.models as mymodels
import STreifen.forms as myforms
from ..models import *
from ..forms import *
import json
import stix2

def stix_report(request, id):
    rep = Report.objects.get(id=id)
    bundle = stix_bundle(rep)
    j = json.dumps(json.loads(str(bundle)), indent=2)
    return HttpResponse(j,  content_type="application/json")

def stix_bundle(rep):
    objects = ()
    for ref in rep.object_refs.all():
        obj = myforms.get_obj_from_id(ref)
        if obj.object_type.name == 'identity':
            i = stix2.Identity(
                id=obj.object_id.object_id,
                name=obj.name,
                identity_class=obj.identity_class,
                description=obj.description,
                #sectors=[str(s.value) for s in obj.sectors.all()],
                sectors=[str(l.value) for l in obj.labels.all()],
                created=obj.created,
                modified=obj.modified,
            )
            objects += (i,)
        elif obj.object_type.name == 'attack-pattern':
            a = stix2.AttackPattern(
                id=obj.object_id.object_id,
                name=obj.name,
                description=obj.description,
                created=obj.created,
                modified=obj.modified,
            )
            objects += (a,)
        elif obj.object_type.name == 'malware':
            m = stix2.Malware(
                id=obj.object_id.object_id,
                name=obj.name,
                description=obj.description,
                labels=[str(l.value) for l in obj.labels.all()],
                created=obj.created,
                modified=obj.modified,
            )
            objects += (m,)
        elif obj.object_type.name == 'threat-actor':
            t = stix2.ThreatActor(
                id=obj.object_id.object_id,
                name=obj.name,
                description=obj.description,
                labels=[str(l.value) for l in obj.labels.all()],
                aliases=[str(a.name) for a in obj.aliases.all()],
                created=obj.created,
                modified=obj.modified,
            )
            objects += (t,)
        elif obj.object_type.name == 'relationship':
            r = stix2.Relationship(
                id=obj.object_id.object_id,
                relationship_type=obj.relationship_type.name,
                description=obj.description,
                source_ref=obj.source_ref.object_id,
                target_ref=obj.target_ref.object_id,
                created=obj.created,
                modified=obj.modified,
            )
            objects += (r,)
        elif obj.object_type.name == 'sighting':
            s = stix2.Sighting(
                id=obj.object_id.object_id,
                sighting_of_ref=obj.sighting_of_ref.object_id,
                where_sighted_refs=[str(w.object_id) for w in obj.where_sighted_refs.all()],
                first_seen=obj.first_seen,
                last_seen=obj.last_seen,
                created=obj.created,
                modified=obj.modified,
            )
            objects += (s,)
    report = stix2.Report(
        id=rep.object_id.object_id,
        labels=[str(l.value) for l in rep.labels.all()],
        name=rep.name,
        description=rep.description,
        published=rep.published,
        object_refs=[str(r.object_id) for r in rep.object_refs.all()],
        created=obj.created,
        modified=obj.modified,
    )
    objects += (report,)
    bundle = stix2.Bundle(*objects)
    return bundle

def report_list(request):
    form = ReportForm()
    if request.method == "POST":
        form = ReportForm(request.POST)
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
            messages.add_message(
                request,
                messages.SUCCESS,
                'Report created -> '+r.name,
            )
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
        return IdentityForm(post)
    elif name == "attack-pattern":
        return AttackPatternForm(post)
    elif name == "malware":
        return MalwareForm(post)
    elif name == "threat-actor":
        return ThreatActorForm(post)
    elif name == "relationship":
        form = RelationshipForm(post)
        if report:
            choices = myforms.object_choices(
                ids=report.object_refs.all().exclude(
                    object_id__startswith = 'relationship'
                ).exclude(
                    object_id__startswith = 'sighting'
                )
            )
            form.fields["source_ref"].choices = choices
            form.fields["target_ref"].choices = choices
        return form
    elif name == "sighting":
        form = SightingForm(post)
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

def add_object_refs(report, oid):
    report.object_refs.add(oid)
    if oid.object_id.split("--")[0] == 'relationship':
        r = get_obj_from_id(oid)
        report.object_refs.add(r.source_ref)
        report.object_refs.add(r.target_ref)
    elif oid.object_id.split("--")[0] == 'sighing':
        r = get_obj_from_id(oid)
        report.object_refs.add(r.sighting_of_ref)
        for wsr in r.where_sighted_of_refs.all():
            report.object_refs.add(wsr)
    return report

def report_view(request, id):
    report = Report.objects.get(id=id)
    stix = stix_bundle(report)
    #print(stix)
    form = ReportForm(instance=report)
    soform = SelectObjectForm()
    selected = None
    aoform = AddObjectForm()
    coform = None
    if request.method == "POST":
        #print(request.POST)
        if 'update' in request.POST:
            form = ReportForm(request.POST, instance=report)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Updated.'
                )
                return redirect("/report/"+id)
        elif 'detach' in request.POST:
            rform = ReportRefForm(request.POST, instance=report)
            #print(rform)
            if rform.is_valid():
                rform.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Updated.'
                )
                return redirect("/report/"+id)
        elif 'delete' in request.POST:
            report.delete()
            messages.add_message(
                request, messages.SUCCESS,
                'Report Deleted -> '+report.name
            )
            return redirect("/report/")
        elif 'select' in request.POST:
            sotid = request.POST.get('select')
            #print(sotid)
            if sotid:
                sot = STIXObjectType.objects.get(id=sotid)
                selected = sot.name
                soform.fields["type"].initial = sotid
                coform = _object_form(selected, report=report)
                aoform.fields["objects"].choices = object_choices(
                    ids=STIXObjectID.objects.filter(
                        object_id__startswith=selected.split("--")[0]
                    )
                )
        elif 'create_obj' in request.POST:
            sotid = request.POST.get('type')
            sot = STIXObjectType.objects.get(id=sotid)
            selected = sot.name
            soform.fields["type"].initial = sotid
            coform = _object_form(sot.name, request=request, report=report)
            if coform.is_valid():
                saved = coform.save()
                #report.object_refs.add(saved.object_id)
                report = add_object_refs(report, saved.object_id)
                report.save()
                redirect("/report/"+id)

        elif 'add_obj' in request.POST:
            aoform = AddObjectForm(request.POST)
            if aoform.is_valid():
                oids = aoform.cleaned_data["objects"]
                for oid in oids:
                    report = add_object_refs(report, oid)
                report.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Updated.'
                )
                redirect("/report/"+id)

    objects = []
    rels = []
    sights = []
    refs = report.object_refs.all().order_by("id")
    relations = Relationship.objects.filter(
        object_id__in=refs
    )
    sightings = Sighting.objects.filter(
        object_id__in=refs
    )
    if selected:
        refs = refs.filter(object_id__startswith=selected)
    for ref in refs:
        o = get_obj_from_id(ref)
        if o.object_type.name == 'sighting':
            sr = [w for w in o.where_sighted_refs.all()]
            sr.append(o.sighting_of_ref)
            for r in sr:
                ro = get_obj_from_id(r)
                if not ro in objects:
                    objects.append(ro)
        elif o.object_type.name == 'relationship':
            #if not o in rels:
            #    rels.append(o)
            for r in (o.source_ref, o.target_ref):
                ro = get_obj_from_id(r)
                if not ro in objects:
                    objects.append(ro)
        else:
            if not o in objects:
                objects.append(o)

    rform = ReportRefForm(instance=report)            
    rform.fields["object_refs"].choices = object_choices(
        report.object_refs.all()
    )

    c = {
        "form": form,
        "soform": soform,
        "selected": selected,
        "coform": coform,
        "aoform": aoform,
        "rform": rform,
        "obj": report,
        "objects": objects,
        #"rels": rels,
        "rels": relations,
        "sights": sightings,
        "stix":stix,
    }
    #return render(request, 'base_view.html', c)
    return render(request, 'report_view.html', c)
