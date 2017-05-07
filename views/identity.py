from django.shortcuts import render, redirect
from django.db.models import Q
import STreifen.models as mymodels
import STreifen.forms as myforms
from ..models import *
from ..forms import *

def identity_list(request):
    """
    identities = Identity.objects.all()
    rels = Relationship.objects.filter(
        Q(source_ref__object_id__startswith='identity')\
        |Q(target_ref__object_id__startswith='identity')\
    )
    print(rels.all())
    """
    form = IdentityForm()
    if request.method == "POST":
        form = IdentityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/identity/")
    c = {
        "form": form,
        #"identities": identities,
    }
    return render(request, 'identity_list.html', c)

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

def _get_related_obj(obj):
    rels = Relationship.objects.filter(
        Q(source_ref__object_id__startswith=obj.object_id)\
        |Q(target_ref__object_id__startswith=obj.object_id)\
    )
    print(rels)
    objects = [obj]
    for rel in rels.all():
        if not rel in objects:
            objects.append(rel)
        o = None
        if rel.source_ref == obj.object_id:
            o = get_obj_from_id(rel.target_ref)
        elif rel.target_ref == obj.object_id:
            o = get_obj_from_id(rel.source_ref)
        if o:
            if not o in objects:
                objects.append(o)
    return objects

def identity_view(request, id):
    identity = Identity.objects.get(id=id)
    form = IdentityForm(instance=identity)
    rels, objects = get_related_obj(identity)
    selected = None
    oform = None
    aoform = AddObjectForm()
    if request.method == "POST":
        #print(request.POST)
        if 'update' in request.POST:
            form = IdentityForm(request.POST, instance=identity)
            if form.is_valid():
                form.save()
                redirect("/identity/"+id)
        elif 'delete' in request.POST:
            #identity.delete()
            return redirect("/identity/")
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
        elif 'add_obj' in request.POST:
            aoform = AddObjectForm(request.POST)
            if aoform.is_valid():
                objs = aoform.cleaned_data["objects"]
                for obj in objs:
                    report.object_refs.add(obj)
                report.save()
                redirect("/report/"+id)

    c = {
        "identity":identity,
        "form": form,
        "selected": selected,
        "oform": oform,
        "aoform": aoform,
        "rels": rels,
        "objects": objects,
    }
    return render(request, 'identity_view.html', c)
