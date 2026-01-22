from laser_prynter import pp

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime

class TestJSONDefault:
    def test_json_default_str(self, capsys):
        'Print a dict as JSON'

        pp.ppd({'a': 'b'}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "b"}'

    def test_json_default_dataclass(self, capsys):
        'Print a dataclass as JSON'

        @dataclass
        class A:
            a: str
        pp.ppd(A('b'), indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "b"}'

    def test_json_default_datetime(self, capsys):
        'Print a datetime as JSON'

        pp.ppd({'a': datetime(2021, 1, 1, 12, 34, 56)}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "2021-01-01T12:34:56"}'

    def test_json_default_class(self, capsys):
        'Print a class instance as JSON'

        class A:
            def __init__(self, a):
                self.a = a
        pp.ppd({'a': A('b')}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": {"a": "b"}}'

    def test_json_default_function(self, capsys):
        'Print a function as JSON'

        def a(): pass

        pp.ppd({'a': a}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "a()"}'

    def test_json_default_slots(self, capsys):
        'Print a class with __slots__ as JSON'

        class A:
            __slots__ = ['a']
            def __init__(self, a):
                self.a = a
        pp.ppd({'a': A('b')}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": {"a": "b"}}'

    def test_json_default_namedtuple(self, capsys):
        'Print a namedtuple as JSON'

        Testr = namedtuple('testr', ('a', 'b'))
        pp.ppd({'x': Testr(1, 2)}, indent=None, style=None)

        captured = capsys.readouterr()

        assert captured.out.strip() == '{"x": {"a": 1, "b": 2}}'

    def test_json_default_list_of_namedtuple(self, capsys):
        'Print a namedtuple as JSON'

        Testr = namedtuple('testr', ('a', 'b'))
        pp.ppd([Testr(1, 2), Testr(3, 4)], indent=None, style=None)

        captured = capsys.readouterr()

        assert captured.out.strip() == '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'

    def test_json_default_other(self, capsys):
        'Print an object with a __str__ method as JSON'

        class Testr:
            def t(self): pass

        t = Testr()
        pp.ppd({'a': t.t}, indent=None, style=None)

        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a": "t"}'

class TestTypeDetection:
    def test_is_namedtuple(self):
        Testr = namedtuple('testr', ('a', 'b'))
        t = Testr(1,2)
        assert pp._isnamedtuple(t) is True

class TestNormaliseNamedTuple:

    def test_normalise(self):
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
