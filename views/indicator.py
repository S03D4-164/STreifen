from django.shortcuts import render, redirect
from django.db.models import Q
from django.forms import formset_factory
import STreifen.models as mymodels
import STreifen.forms as myforms
from ..models import *
from ..forms import *
from .chart import *
from collections import OrderedDict
import json

def indicator_list(request):
    form = IndicatorForm()
    PatternFormSet = formset_factory(PatternForm, extra=2)
    pformset = PatternFormSet()
    print(pformset)
    if request.method == "POST":
        if 'create' in request.POST:
            form = IndicatorForm(request.POST)
            pformset = PatternFormSet(request.POST)
            if form.is_valid():
                i = form.save()
                if pformset.is_valid():
                    for pform in pformset:
                        p = pform.save()
                        if p:
                            i.pattern.add(p)
                if i:
                    i.save()
                return redirect("/indicator/")
        #if "select_pset":
            
    c = {
        "objtype":"indicator",
        "form": form,
        "pformset": pformset,
    }
    #return render(request, 'base_list.html', c)
    return render(request, 'indicator_list.html', c)

def indicator_view(request, id):
    indicator = Indicator.objects.get(id=id)
    form = MalwareForm(instance=malware)

    rels, objects = get_related_obj(indicator)
    sights = Sighting.objects.filter(
        sighting_of_ref=malware.object_id
    )
    for sight in sights:
        for wsr in sight.where_sighted_refs.all():
            w = get_obj_from_id(wsr)
            if not w in objects:
                objects.append(w)
    atform = AddObjectForm()
    if request.method == "POST":
        if 'update' in request.POST:
            form = MalwareForm(request.POST, instance=malware)
            if form.is_valid():
                form.save()
                redirect("/malware/"+id)
        elif 'delete' in request.POST:
            #malware.delete()
            return redirect("/malware/")
        elif 'relation' in request.POST:
            rid = request.POST.get('relation')
            r = DefinedRelationship.objects.get(id=rid)
            source_ref = None
            target_ref = None
            rel_type = r.type
            if r.source == actor.object_type:
                oform = _object_form(r.target.name, request=request)
                source_ref = actor.object_id
            elif r.target == actor.object_type:
                oform = _object_form(r.source.name, request=request)
                target_ref = actor.object_id
            drform.fields["relation"].initial = rid
            if 'create_obj' in request.POST:
                if oform.is_valid():
                    created = oform.save
                    if not source_ref:
                        source_ref = created.object_id
                    elif not target_ref:
                        target_ref = created.object_id
                    Relationship.objects.create(
                        source_ref = source_ref,
                        target_ref = target_ref,
                        relationship_type = rel_type,
                    )
                    redirect("/actor/"+id)
        elif 'add_tgt' in request.POST:
            atform = AddObjectForm(request.POST)
            if atform.is_valid():
                tgts = atform.cleaned_data["objects"]
                rtype = RelationshipType.objects.get(name='targets')
                for tgt in tgts:
                    r, created = Relationship.objects.get_or_create(
                        source_ref = malware.object_id,
                        relationship_type = rtype,
                        target_ref = tgt,
                    )
                redirect("/malware/"+id)
    atform.fields["objects"].choices = object_choices(
        ids=STIXObjectID.objects.filter(
            object_id__startswith='identity'
        )
    )
    c = {
        "form": form,
        #"selected": selected,
        #"oform": oform,
        "atform": atform,
        "obj": indicator,
        "rels": rels,
        "sights": sights,
        "objects":objects,
    }
    #return render(request, 'malware_view.html', c)
    return render(request, 'base_view.html', c)
