import json
import logging
from typing import Any

from laser_prynter.log import LogFormatter


def _make_record(
    name: str = 'test', level: int = logging.INFO, msg: str = '', args: Any = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name=name, level=level, pathname='', lineno=0,
        msg=msg, args=None, exc_info=None,
    )
    if args is not None:
        record.args = args
    return record


def _format(record: logging.LogRecord, **kwargs: Any) -> dict[str, Any]:
    formatter = LogFormatter(**kwargs)
    output = formatter.format(record)
    return json.loads(output)  # type: ignore[no-any-return]


class TestLaserPrynterStyle:
    """G2: existing laser-prynter call conventions produce identical output."""

    def test_plain_message(self) -> None:
        record = _make_record(msg='This is a basic info message')
        result = _format(record)
        assert result['msg'] == 'This is a basic info message'
        assert result['event'] == {}

    def test_single_dict_context(self) -> None:
        record = _make_record(msg='This is an info message', args={'key': 'value'})
        result = _format(record)
        assert result['msg'] == 'This is an info message'
        assert result['event'] == {'key': 'value'}

    def test_positionals_with_trailing_dict(self) -> None:
        record = _make_record(msg='This is a debug message', args=('arg1', 'arg2', {'key': 'value'}))
        result = _format(record)
        assert result['msg'] == 'This is a debug message'
        assert result['event'] == {'args': ['arg1', 'arg2'], 'key': 'value'}


class TestStdlibPercentStyle:
    """G1: stdlib %-style records are fully rendered."""

    def test_uvicorn_startup(self) -> None:
        record = _make_record(
            name='uvicorn.error',
            msg='Uvicorn running on %s://%s:%d (Press CTRL+C to quit)',
            args=('http', '0.0.0.0', 8000),
        )
        result = _format(record)
        assert result['msg'] == 'Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)'
        assert result['event'] == {}
        assert '%s' not in result['msg']
        assert '%d' not in result['msg']

    def test_uvicorn_access_structured(self) -> None:
        record = _make_record(
            name='uvicorn.access',
            msg='%s - "%s %s HTTP/%s" %s',
            args=('127.0.0.1:5000', 'GET', '/health', '1.1', 200),
        )
        result = _format(record)
        assert result['event']['client'] == '127.0.0.1:5000'
        assert result['event']['method'] == 'GET'
        assert result['event']['path'] == '/health'
        assert result['event']['http_version'] == '1.1'
        assert result['event']['status'] == 200
        assert '%s' not in result['msg']

    def test_uvicorn_access_fields_disabled(self) -> None:
        record = _make_record(
            name='uvicorn.access',
            msg='%s - "%s %s HTTP/%s" %s',
            args=('127.0.0.1:5000', 'GET', '/health', '1.1', 200),
        )
        result = _format(record, access_fields=False)
        assert result['event'] == {}
        assert '127.0.0.1:5000' in result['msg']
        assert '200' in result['msg']

    def test_stdlib_string_format_args(self) -> None:
        record = _make_record(msg='Connected to %s on port %d', args=('localhost', 5432))
        result = _format(record)
        assert result['msg'] == 'Connected to localhost on port 5432'
        assert result['event'] == {}

    def test_no_args(self) -> None:
        record = _make_record(msg='Simple message', args=None)
        result = _format(record)
        assert result['msg'] == 'Simple message'
        assert result['event'] == {}

    def test_empty_tuple_args(self) -> None:
        record = _make_record(msg='Simple message', args=())
        result = _format(record)
        assert result['msg'] == 'Simple message'
        assert result['event'] == {}


class TestEdgeCases:
    """Documented caveats and edge cases."""

    def test_lone_dict_arg_treated_as_context(self) -> None:
        """Caveat: a stdlib caller whose final %-arg is a dict gets read as context."""
        record = _make_record(msg='payload=%s', args=({'a': 1},))
        result = _format(record)
        assert result['msg'] == 'payload=%s'
        assert result['event'] == {'a': 1}

    def test_defaults_included_as_context(self) -> None:
        record = _make_record(msg='hi')
        result = _format(record, defaults={'service': 'web'})
        assert result['context'] == {'service': 'web'}

    def test_defaults_none(self) -> None:
        record = _make_record(msg='hi')
        result = _format(record, defaults=None)
        assert 'context' not in result

    def test_access_fields_non_access_logger(self) -> None:
        """5-tuple on a non-access logger is treated as stdlib %-style."""
        record = _make_record(
            name='myapp.server',
            msg='%s %s %s %s %s',
            args=('a', 'b', 'c', 'd', 'e'),
        )
        result = _format(record)
        assert result['msg'] == 'a b c d e'
        assert result['event'] == {}
