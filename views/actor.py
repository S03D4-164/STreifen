from django.shortcuts import render, redirect
from django.db.models import Q
import STreifen.models as mymodels
import STreifen.forms as myforms
from ..models import *
from ..forms import *
import stix2

def actor_list(request):
    actors = ThreatActor.objects.all()
    labels = {}
    for actor in actors:
        for label in actor.labels.all():
            if not label.value in labels:
                labels[label.value] = 1
            else:
                labels[label.value] += 1
    #print(labels)
    rels = Relationship.objects.filter(
        Q(source_ref__object_id__startswith='threat-actor')\
        |Q(target_ref__object_id__startswith='threat-actor')\
    )
    #print(rels.all())
    form = ThreatActorForm()
    if request.method == "POST":
        if 'create' in request.POST:
            form = ThreatActorForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("/actor/")
    c = {
        "form": form,
        "actors": actors,
        #"labels": labels,
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
    rels = Relationship.objects.filter(
        Q(source_ref__object_id__startswith=actor.object_id)\
        |Q(target_ref__object_id__startswith=actor.object_id)\
    )
    print(rels)
    objects = [actor]
    for rel in rels.all():
        obj = None
        if rel.source_ref == actor.object_id:
            obj = get_obj_from_id(rel.target_ref)
        elif rel.target_ref == actor.object_id:
            obj = get_obj_from_id(rel.source_ref)
        if obj:
            if not obj in objects:
                objects.append(obj)
    print(objects)
    #stix = stix_report(actor)
    #print(stix)
    drs = DefinedRelationship.objects.filter(
        Q(source=actor.object_type)\
        |Q(target=actor.object_type)
    )
    #print(drs)
    drform = DefinedRelationshipForm()
    drform.fields["relation"].queryset = drs
    selected = None
    oform = None
    atform = AddObjectForm()
    atform.fields["objects"].choices = object_choices(
        ids=STIXObjectID.objects.filter(
            object_id__startswith='identity'
        )
    )
    if request.method == "POST":
        #print(request.POST)
        if 'update' in request.POST:
            form = ThreatActorForm(request.POST, instance=actor)
            if form.is_valid():
                form.save()
                redirect("/actor/"+id)
        elif 'delete' in request.POST:
            actor.delete()
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
    c = {
        "form": form,
        "drform": drform,
        "selected": selected,
        "oform": oform,
        "atform": atform,
        "actor": actor,
        "rels": rels,
        "objects":objects,
    }
    return render(request, 'actor_view.html', c)
