from django import forms
from .models import *
import STreifen.models as mymodels

class CreateRelationshipForm(forms.ModelForm):
    class Meta:
        model = Relationship
        fields = [
            "source_ref",
            "relationship_type",
            "target_ref",
            "description",
        ]

class CreateSightingForm(forms.ModelForm):
    class Meta:
        model = Sighting
        fields = [
            "where_sighted_refs",
            "sighting_of_ref",
            "first_seen",
            "last_seen",
        ]

class CreateThreatActorForm(forms.ModelForm):
    class Meta:
        model = ThreatActor
        fields = [
            "name",
            "description",
            "labels",
            "aliases",
        ]

class CreateMalwareForm(forms.ModelForm):
    class Meta:
        model = Malware
        fields = [
            "name",
            "description",
            "labels",
        ]

class CreateAttackPatternForm(forms.ModelForm):
    class Meta:
        model = AttackPattern
        fields = [
            "name",
            "description",
        ]

class CreateIdentityForm(forms.ModelForm):
    class Meta:
        model = Identity
        fields = [
            "name",
            "identity_class",
            "sectors",
            "description",
        ]

class SelectObjectForm(forms.Form):
    type = forms.ModelChoiceField(
        queryset=STIXObjectType.objects.filter(
            name__in=[
                "identity",
                "attack-pattern",
                "malware",
                "threat-actor",
                "relationship",
                "sighting",
            ]
        ),
    )

def get_obj_from_id(soi):
    sot = soi.object_id.split('--')[0]
    m = ""
    for s in sot.split('-'):
        m += s.capitalize()
    obj = getattr(mymodels, m).objects.get(object_id=soi)
    return obj

def object_choices(ids=STIXObjectID.objects.all()):
    choices = ()
    for soi in ids:
        obj = get_obj_from_id(soi)
        name = ""
        if obj.object_type.name == 'relationship':
            src = get_obj_from_id(obj.source_ref)
            tgt = get_obj_from_id(obj.target_ref)
            rel = obj.relationship_type.name
            name = " ".join([src.name, rel, tgt.name])
        elif obj.object_type.name == 'sighting':
            sor = get_obj_from_id(obj.sighting_of_ref)
            tgt = []
            for wsr in obj.where_sighted_refs.all():
                i = get_obj_from_id(wsr)
                tgt.append(i.name)
            name = ",".join(tgt) + " sighted " + sor.name
        else:
            name = obj.name
        choices += ((
            obj.object_id.id,
            obj.object_type.name + " : " + name,
        ),)
    return choices

class AddObjectForm(forms.Form):
    objects = forms.ModelMultipleChoiceField(
        queryset=STIXObjectID.objects.all()
    )
    def __init__(self, *args, **kwargs):
        super(AddObjectForm, self).__init__(*args, **kwargs)
        self.fields["objects"].choices = object_choices()

class CreateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            "name",
            "labels",
            "description",
            "published",
            "object_refs",
        ]
        widgets = {
            "labels":forms.CheckboxSelectMultiple(),
            "object_refs":forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        super(CreateReportForm, self).__init__(*args, **kwargs)
        self.fields["labels"].required = False
        self.fields["description"].required = False
        self.fields["published"].required = False
        self.fields["object_refs"].required = False

class TypeSelectForm(forms.Form):
    types = forms.ModelMultipleChoiceField(
        queryset=STIXObjectType.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    relation = forms.ModelMultipleChoiceField(
        queryset=RelationshipType.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
    def __init__(self, *args, **kwargs):
        super(TypeSelectForm, self).__init__(*args, **kwargs)
        self.fields["types"].required = False
        self.fields["relation"].required = False
