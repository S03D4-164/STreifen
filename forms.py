from django import forms
from .models import *

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
