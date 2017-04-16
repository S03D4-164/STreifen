from django.contrib import admin

from .models import *

admin.site.register(STIXObjectType)
admin.site.register(STIXObjectID)
admin.site.register(RelationshipType)
admin.site.register(DefinedRelationship)
admin.site.register(ReportLabel)
admin.site.register(Report)

