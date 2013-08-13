'''
Created on 23-07-2013

@author: kamil
'''
import unittest
import mock

from filthy.views import FilterMixin
from filthy.exceptions import FilterValueError


class FilterMixinTestCase(unittest.TestCase):
    
    def test_build_kwarg1(self):
        """
        Should handle not-negated kwargs gracefuly
        """
        key = "id"
        fm = FilterMixin()
        self.assertEquals(("id", False), fm.build_kwarg(key))
    
    def test_build_kwarg2(self):
        """
        Should handle negated kwargs gracefuly
        """
        key = "!id"
        fm = FilterMixin()
        self.assertEquals(("!id", True), fm.build_kwarg(key))
    
    def test_build_kwargs(self):
        """
        Should build all kwargs based on values returned by filter.items()
        """
        filters = mock.Mock()
        filter_dict = {
            "id": ("id__exact", lambda val: "lambda_id"),
            "id_lt": ("id__lt", lambda val: "lambda_id_lt"),
            "text_startswith": ("text__startswith", lambda val: "lambda_text")
        }
        filters.items.return_value = filter_dict.items()
        filters.keys.return_value = filter_dict.keys()
        fm = FilterMixin()
        query_params = {"id_lt": 10, "!id_lt": 5, "!text_startswith": "What up?!"}
        expected = (
            ("id__lt", "lambda_id_lt", False),
            ("id__lt", "lambda_id_lt", True),
            ("text__startswith", "lambda_text", True)
        )
        actual = fm.build_search_kwargs(filters, query_params)
        self.assertSetEqual(set(expected), actual)
    
    def test_build_kwargs2(self):
        """
        Should raise FilterValueError when transformation of query param fails
        """
        filters = mock.Mock()
        raising_callable = mock.Mock()
        raising_callable.side_effect = ValueError()
        filter_dict = {
            "id": ("id__exact", lambda val: "lambda_id"),
            "id_lt": ("id__lt", lambda val: "lambda_id_lt"),
            "text_startswith": ("text__startswith", raising_callable)
        }
        filters.items.return_value = filter_dict.items()
        filters.keys.return_value = filter_dict.keys()
        fm = FilterMixin()
        query_params = {"id_lt": 10, "!id_lt": 5, "!text_startswith": "What up?!"}
        with self.assertRaises(FilterValueError):
            fm.build_search_kwargs(filters, query_params)
    
    def test_generate_possible_kwargs(self):
        """
        Should negate all possible kwargs and join with not negated
        """
        filters = mock.Mock()
        filters.keys.return_value = ["h", "w"]
        fm = FilterMixin()
        self.assertListEqual(["h", "w", "!h", "!w"], fm.generate_possible_kwargs(filters))
    
    def test_filter_with_search_kwarg1(self):
        qs = mock.Mock()
        kwarg = ('id__lt', 10, False)
        fm = FilterMixin()
        fm.filter_with_search_kwarg(qs, kwarg)
        qs.filter.assert_called_once_with(id__lt=10)
    
    def test_filter_with_search_kwarg2(self):
        qs = mock.Mock()
        kwarg = ('id__lt', 10, True)
        fm = FilterMixin()
        fm.filter_with_search_kwarg(qs, kwarg)
        qs.exclude.assert_called_once_with(id__lt=10)
        
    def test_get_queryset(self):
        qs = mock.Mock()
        
        class BaseView(object):
            def get_queryset(self):
                return qs
            
        class MyView(FilterMixin, BaseView):
            filters = {
                "id": ("id__exact", lambda v: int(v)),
                "name": ("name__exact", lambda v: str(v)),
                "age": ("age__exact", lambda v: int(v)),
            }

        class StubRequest:
            def __init__(self, dct):
                self.QUERY_PARAMS = dct
        
        view = MyView()
        view.request = StubRequest({"id": 1, "!age": 18, "age": 20})
        
        with mock.patch.object(view, 'filter_with_search_kwarg'): #@UndefinedVariable
            view.get_queryset()
            self.assertEquals(3, view.filter_with_search_kwarg.call_count)