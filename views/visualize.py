from django.shortcuts import redirect, render
from django.db.models import Q
from django.utils.safestring import SafeString

from ..models import *
from ..forms import *
import json

def vis_drs(request):
    tsform = TypeSelectForm()
    nodes = []
    edges = []
    drs = None
    if request.method == "POST":
        tsform = TypeSelectForm(request.POST)
        if tsform.is_valid():
            types = tsform.cleaned_data["types"]
            print(types)
            rels = tsform.cleaned_data["relation"]
            print(rels)
            drs = DefinedRelationship.objects.exclude(
                type__in=rels
            ).exclude(
                Q(source__in=types)|Q(target__in=types),
            )
    if not drs: 
        drs = DefinedRelationship.objects.all()
    for dr in drs:
        for sot in (dr.source, dr.target):
            node = {
                'id': sot.id,
                'label': sot.name,
            }
            if not node in nodes:
                nodes.append(node)
        edge = {
            'from': dr.source.id,
            'to': dr.target.id,
            'label': dr.type.name,
        }
        if not edge in edges:
            edges.append(edge)
    dataset = {
        'nodes': nodes,
        'edges': edges,
        'tsform':tsform,
    }
    return render(request, "visualize_view.html", dataset)
        
