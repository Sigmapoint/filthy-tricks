'''
Created on 23-07-2013

@author: kamil
'''  
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.fields import WritableField

from filthy.views import TrackDependencyMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist

class TrackDependencyPrimaryKeyField(PrimaryKeyRelatedField):
    
    errors = {
        "no_context": u"Serializers using TrackDependencyPrimaryKeyField must get context.",
        "no_view": u"Serializers using TrackDependencyPrimaryKeyField must"
                   " receive current view passed as `view` in context.",
        "wrong_view": u"Serializers using TrackDependencyPrimaryKeyField must"
                   " be used by views that mix in TrackDependenciesMixin"
    }
    
    def initialize(self, parent, field_name):
        """
        Called to set up a field prior to field_to_native or field_from_native.

        parent - The parent serializer.
        model_field - The model field this field corresponds to, if one exists.
        """
        super(TrackDependencyPrimaryKeyField, self).initialize(parent, field_name)
        assert "view" in self.root.context, self.__class__.errors["no_view"]
        assert isinstance(self.root.context["view"], TrackDependencyMixin)
    
    def field_to_native(self, obj, field_name):
        try:
            tracked = getattr(obj, self.source or field_name)
            skiptrack = False
        except (ObjectDoesNotExist, AttributeError):
            skiptrack = True
        res = super(TrackDependencyPrimaryKeyField, self).field_to_native(
            obj,
            field_name
        )
        if not skiptrack:
            if self.queryset:
                key = self.queryset.model
            elif not self.many:
                key = tracked.__class__
            else:
                key = tracked.model
            self.root.context["view"].track(key, res)
        return res

class ListField(WritableField):
    
    def validate(self, value):
        super(ListField, self).validate(value)
        if not isinstance(value, list):
            raise ValidationError("Expecting list.")
    
    def to_native(self, obj):
        return obj

    def from_native(self, data):
        return data

class TrackDependencyListField(ListField):
    
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        assert self.model is not None, "TrackDependencyListField must receive `model` kwarg."
        super(TrackDependencyListField, self).__init__(*args, **kwargs)
        
    def field_to_native(self, obj, field_name):
        res = super(TrackDependencyListField, self).field_to_native(
            obj,
            field_name
        )
        key = self.model
        self.root.context["view"].track(key, res)
        return res