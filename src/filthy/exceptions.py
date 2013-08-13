'''
Created on 23-07-2013

@author: kamil
'''
from django.utils.translation import gettext as _

from rest_framework.exceptions import APIException

class FilterValueError(APIException):
    
    DETAIL = _(u"Parsing query parameter for filtering failed.")
    
    def __init__(self, status_code=400, detail=DETAIL):
        self.status_code = status_code
        self.detail = detail

class DependencyTrackingCollision(Exception):
    pass