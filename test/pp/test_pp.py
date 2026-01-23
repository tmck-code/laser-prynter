from laser_prynter import pp

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from io import StringIO

class TestJSONDefault:
    def test_str(self):
        'Print a dict as JSON'

        s = StringIO()
        pp.ppd({'a': 'b'}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": "b"}'

    def test_dataclass(self):
        'Print a dataclass as JSON'

        s = StringIO()
        @dataclass
        class A:
            a: str

        pp.ppd(A('b'), indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": "b"}'

    def test_datetime(self):
        'Print a datetime as JSON'

        s = StringIO()
        pp.ppd({'a': datetime(2021, 1, 1, 12, 34, 56)}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": "2021-01-01T12:34:56"}'

    def test_class(self):
        'Print a class instance as JSON'

        s = StringIO()
        class A:
            def __init__(self, a):
                self.a = a

        pp.ppd({'a': A('b')}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": {"a": "b"}}'

    def test_function(self):
        'Print a function as JSON'

        s = StringIO()
        def a(): pass

        pp.ppd({'a': a}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": "a()"}'

    def test_slots(self):
        'Print a class with __slots__ as JSON'

        s = StringIO()
        class A:
            __slots__ = ['a']
            def __init__(self, a):
                self.a = a
        pp.ppd({'a': A('b')}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": {"a": "b"}}'

    def test_namedtuple(self):
        'Print a namedtuple as JSON'

        s = StringIO()
        Testr = namedtuple('testr', ('a', 'b'))

        pp.ppd({'x': Testr(1, 2)}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"x": {"a": 1, "b": 2}}'

    def test_list_of_namedtuple(self):
        'Print a namedtuple as JSON'

        s = StringIO()
        Testr = namedtuple('testr', ('a', 'b'))
        pp.ppd([Testr(1, 2), Testr(3, 4)], indent=None, style=None, file=s)

        assert s.getvalue().strip() == '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'

    def test_other(self):
        'Print an object with a __str__ method as JSON'

        s = StringIO()
        class Testr:
            def t(self): pass

        t = Testr()
        pp.ppd({'a': t.t}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"a": "t"}'

    def test_tuple_keys(self):
        'Print a dict with tuple keys as JSON'

        s = StringIO()
        pp.ppd({('a', 'b'): 'c'}, indent=None, style=None, file=s)

        assert s.getvalue().strip() == '{"(\'a\', \'b\')": "c"}'



class TestNormalise:

    def test_is_namedtuple(self):
        'Detect if an object is a namedtuple'

        Testr = namedtuple('testr', ('a', 'b'))
        t = Testr(1,2)

        assert pp._isnamedtuple(t) is True

    def test_normalise(self):
        'Normalise namedtuples into dicts'

        Testr = namedtuple('testr', ('a', 'b'))

        result = pp._normalise({
            'x': Testr(1, 2),
            'y': [Testr(5, 6), Testr(3, 4)],
        })

        assert result == {
            'x': {'a': 1, 'b': 2},
            'y': [
                {'a': 5, 'b': 6},
                {'a': 3, 'b': 4},
            ]
        }

