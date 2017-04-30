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
    object_id = models.OneToOneField(STIXObjectID, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    #createdby_ref = models.ForeignKey(STIXObjectID, related_name="createdby_ref")
    #object_marking_ref = models.ForeignKey(MarkingObjectID)
    class Meta:
        unique_together = (("object_type", "object_id"),)
        ordering = ["object_type", "object_id"]
    def delete(self):
        STIXObjectID.objects.get(object_id=self.object_id).delete()
        

class ReportLabel(models.Model):
    value = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.value
    class Meta:
        ordering = ["value"]

def _set_id(obj, name):
    from uuid import uuid4
    if not obj.object_type:
        s = STIXObjectType.objects.filter(name=name)
        if s.count() == 1:
            obj.object_type = STIXObjectType.objects.get(name=name)
    if obj.object_type and not obj.object_id:
        soi = STIXObjectID.objects.create(
            object_id = obj.object_type.name + "--" + str(uuid4())
        )
        obj.object_id = soi
    return obj

class Report(STIXObject):
    name = models.CharField(max_length=250, unique=True)
    labels = models.ManyToManyField(ReportLabel, blank=True)
    description = models.TextField(blank=True, null=True)
    published = models.DateTimeField(blank=True, null=True)
    object_refs = models.ManyToManyField(STIXObjectID, blank=True)
    def save(self, *args, **kwargs):
        self = _set_id(self, 'report')
        super(Report, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class IdentityLabel(models.Model):
    value = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.value
    class Meta:
        ordering = ["value"]

class IndustrySector(models.Model):
    value = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.value
    class Meta:
        ordering = ["value"]

class Identity(STIXObject):
    IDENTITY_CLASS_CHOICES = {
        ('individual','individual'),
        ('group','group'),
        ('organization','organization'),
        ('class','class'),
        ('unknown','unknown'),
    }
    name = models.CharField(max_length=250,unique=True)
    identity_class = models.CharField(max_length=250, choices=IDENTITY_CLASS_CHOICES)
    #identity_class = models.ForeignKey(IdentityClass, blank=True)
    description = models.TextField(blank=True, null=True)
    sectors = models.ManyToManyField(IndustrySector, blank=True)
    labels = models.ManyToManyField(IdentityLabel, blank=True)
    def save(self, *args, **kwargs):
        self = _set_id(self, 'identity')
        super(Identity, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class AttackPattern(STIXObject):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    #external_references = models.ManyToManyField(ExternalReference, blank=True)
    def save(self, *args, **kwargs):
        self = _set_id(self, 'attack-pattern')
        super(AttackPattern, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class MalwareLabel(models.Model):
    value = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.value
    class Meta:
        ordering = ["value"]

class Malware(STIXObject):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    labels = models.ManyToManyField(MalwareLabel, blank=True)
    def save(self, *args, **kwargs):
        self = _set_id(self, 'malware')
        super(Malware, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class ThreatActorLabel(models.Model):
    value = models.CharField(max_length=250, unique=True)
    def __str__(self):
        return self.value
    class Meta:
        ordering = ["value"]

class ThreatActorAlias(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class ThreatActor(STIXObject):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    labels = models.ManyToManyField(ThreatActorLabel, blank=True)
    aliases = models.ManyToManyField(ThreatActorAlias, blank=True)
    def save(self, *args, **kwargs):
        self = _set_id(self, 'threat-actor')
        super(ThreatActor, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class Relationship(STIXObject):
    source_ref= models.ForeignKey(STIXObjectID, related_name='source_ref')
    target_ref = models.ForeignKey(STIXObjectID, related_name='target_ref')
    relationship_type = models.ForeignKey(RelationshipType)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        src = self.source_ref.object_id
        tgt = self.target_ref.object_id
        rel = self.relationship_type.name
        return " ".join([src, rel, tgt])
    def save(self, *args, **kwargs):
        self = _set_id(self, 'relationship')
        super(Relationship, self).save(*args, **kwargs)

class Sighting(STIXObject):
    first_seen = models.DateTimeField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    sighting_of_ref= models.ForeignKey(STIXObjectID, related_name='sighting_of_ref')
    where_sighted_refs = models.ManyToManyField(STIXObjectID, related_name='where_sighted_ref')
    #observed_data_refs = models.ManyToManyField(STIXObjectID, related_name='observed_data_refs')
    def save(self, *args, **kwargs):
        self = _set_id(self, 'sighting')
        super(Sighting, self).save(*args, **kwargs)
