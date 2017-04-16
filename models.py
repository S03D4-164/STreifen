from django.db import models

class STIXObjectType(models.Model):
    name = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class MarkingDefinitionObjectType(models.Model):
    name = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class STIXObjectID(models.Model):
    object_id = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.object_id
    class Meta:
        ordering = ["object_id"]

class RelationshipType(models.Model):
    name = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class DefinedRelationship(models.Model):
    type = models.ForeignKey(RelationshipType)
    source = models.ForeignKey(STIXObjectType, related_name='source')
    target = models.ForeignKey(STIXObjectType, related_name='target')
    def __str__(self):
        drs = self.source.name + " " + self.type.name + " " + self.target.name
        return drs
    class Meta:
        unique_together = (("source", "type", "target"),)
        ordering = ["source", "type", "target"]

class STIXObject(models.Model):
    object_type = models.ForeignKey(STIXObjectType, blank=True, null=True)
    object_id = models.ForeignKey(STIXObjectID, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    #createdby_ref = models.ForeignKey(STIXObjectID, related_name="createdby_ref")
    #object_marking_ref = models.ForeignKey(MarkingObjectID)
    class Meta:
        unique_together = (("object_type", "object_id"),)
        ordering = ["object_type", "object_id"]

class ReportLabel(models.Model):
    value = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.value
    class Meta:
        ordering = ["value"]

from uuid import uuid4
class Report(STIXObject):
    name = models.CharField(max_length=250)
    labels = models.ManyToManyField(ReportLabel, blank=True)
    description = models.TextField(blank=True, null=True)
    published = models.DateTimeField(blank=True, null=True)
    object_refs = models.ManyToManyField(STIXObjectID, blank=True)
    def save(self, *args, **kwargs):
        if not self.object_type:
            s = STIXObjectType.objects.filter(name="report")
            if s.count() == 1:
                self.object_type = STIXObjectType.objects.get(name="report")
        if not self.object_id:
            soi = STIXObjectID.objects.create(
                object_id = "report--" + str(uuid4())
            )
            self.object_id = soi

        super(Report, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]
