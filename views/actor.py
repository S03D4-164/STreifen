from django.shortcuts import render, redirect
from django.db.models import Q
import STreifen.models as mymodels
import STreifen.forms as myforms
from ..models import *
from ..forms import *
from collections import OrderedDict

def actor_viz(request, id=None):
    rels = Relationship.objects.filter(
        Q(source_ref__object_id__startswith='threat-actor')\
        |Q(target_ref__object_id__startswith='threat-actor')\
    )
    data = target_stats(rels, id)
    c = {
        "data": data,
    }
    return render(request, 'actor_viz.html', c)

def target_stats(rels, id=None):
    ati = rels.filter(
        source_ref__object_id__startswith='threat-actor',
        relationship_type__name='targets',
        target_ref__object_id__startswith='identity',
    )
    if id:
        actor = ThreatActor.objects.get(id=id)
        ati = ati.filter(source_ref__object_id=actor.object_id)
    data = {}
    for a in ati.all():
        act = get_obj_from_id(a.source_ref)
        if not act.name in data:
            data[act.name] = {
                "inner":{},
                "value":0,
            }
        tgt = get_obj_from_id(a.target_ref)
        if tgt:
            data[act.name]["value"] += 1
            label = tgt.labels.all()
            if label:
                if not label[0].value in data[act.name]["inner"]:
                    data[act.name]["inner"][label[0].value] = 1
                else:
                    data[act.name]["inner"][label[0].value] += 1
    for d in data.items():
        d[1]["inner"] = OrderedDict(
            sorted(
                d[1]["inner"].items(),
                key=lambda kv:kv[1],
                reverse=True
            )
        )
    data = OrderedDict(
        sorted(
            data.items(),
            key=lambda kv: kv[1]["value"],
            reverse=True
        )
    )
    return data

def actor_list(request):
    rels = Relationship.objects.filter(
        Q(source_ref__object_id__startswith='threat-actor')\
        |Q(target_ref__object_id__startswith='threat-actor')\
    )
    data = target_stats(rels)
    form = ThreatActorForm()
    if request.method == "POST":
        if 'create' in request.POST:
            form = ThreatActorForm(request.POST)
            if form.is_valid():
                a = form.save()
                taa, created = ThreatActorAlias.objects.get_or_create(
                    name = a.name
                )
                a.aliases.add(taa)
                a.save()
                return redirect("/actor/")
    c = {
        "form": form,
        "rels": rels,
        "data": data,
    }
    return render(request, 'actor_list.html', c)

def _object_form(name, request=None, actor=None):
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
    return False

def actor_view(request, id):
    actor = ThreatActor.objects.get(id=id)
    form = ThreatActorForm(instance=actor)

    rels, objects = get_related_obj(actor)
    #selected = None
    #oform = None
    atform = AddObjectForm()
    if request.method == "POST":
        #print(request.POST)
        if 'update' in request.POST:
            form = ThreatActorForm(request.POST, instance=actor)
            if form.is_valid():
                form.save()
                redirect("/actor/"+id)
        elif 'delete' in request.POST:
            #actor.delete()
            return redirect("/actor/")
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
                    Relationship.objects.get_or_create(
                        source_ref = actor.object_id,
                        relationship_type = rtype,
                        target_ref = tgt,
                    )
                redirect("/actor/"+id)
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
        "actor": actor,
        #"obj": actor,
        "rels": rels,
        "objects":objects,
    }
    return render(request, 'actor_view.html', c)
    #return render(request, 'base_view.html', c)
