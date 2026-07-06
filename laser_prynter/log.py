'''
A module to create loggers with custom handlers and a custom formatter.

usage examples to initialise a logger:
    ```python
    # 1. initialise logger to stderr:
    logger = getLogger('my_logger', level=logging.DEBUG, stream=sys.stderr)

    # 2. initialise logger to file:
    logger = getLogger('my_logger', level=logging.DEBUG, filename='my_log.log')

    # 3. initialise logger to both stderr and file:
    logger = getLogger('my_logger', level=logging.DEBUG, stream=sys.stderr, files={LogLevel.INFO: 'info.log'})
    ```

usage examples to log messages:
    ```python
    logger.info('This is a basic info message')
    # {"timestamp": "2024-12-09T15:05:43.904417+10:00", "msg": "This is a basic info message", "event": {}}

    logger.info('This is an info message', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904600+10:00", "msg": "This is an info message", "event": {"key": "value"}}

    logger.debug('This is a debug message', 'arg1', 'arg2', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904749+10:00", "msg": "This is a debug message", "event": {"args": ["arg1", "arg2"], "key": "value"}}

    # stdlib / third-party loggers (e.g. uvicorn) using %-style formatting
    # are rendered automatically — no subclass needed:
    #   logging.getLogger('uvicorn').info('Listening on %s:%d', '0.0.0.0', 8000)
    #   # {"timestamp": "...", "msg": "Listening on 0.0.0.0:8000", "event": {}}
    ```
'''

import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import TextIO

from laser_prynter.pp import _json_default


class LogLevel:
    'An enum type for log levels.'
    CRITICAL = logging.CRITICAL
    ERROR    = logging.ERROR
    WARNING  = logging.WARNING
    INFO     = logging.INFO
    DEBUG    = logging.DEBUG
    NOTSET   = logging.NOTSET


DEFAULT_LOG_LEVEL = LogLevel.INFO

class LogFormatter(logging.Formatter):
    'Custom log formatter that formats log messages as JSON, aka "Structured Logging".'

    def __init__(self, defaults: dict | None = None, access_fields: bool = True):
        '''
        Initializes the log formatter with optional default context.
        - `defaults` is a dictionary of default context values to include in every log message.
        - `access_fields` promotes uvicorn access-log tuples to structured event fields.
        '''
        self.defaults = defaults or {}
        self.access_fields = access_fields
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        'Formats the log message as JSON.'
        message, event = self._render(record)
        payload = {
            'timestamp': datetime.now().astimezone().isoformat(),
            'level':     record.levelname,
            'name':      record.name,
            'msg':       message,
            'event':     event,
            **({'context': self.defaults} if self.defaults else {}),
        }
        record.msg = json.dumps(payload, default=_json_default)
        record.args = ()
        return super().format(record)

    def _render(self, record: logging.LogRecord) -> tuple[str, dict]:
        args = record.args

        if self.access_fields and record.name.endswith('access') \
                and isinstance(args, tuple) and len(args) == 5:
            client, method, path, http_version, status = args
            return record.getMessage(), {
                'client': client, 'method': method, 'path': path,
                'http_version': http_version, 'status': status,
            }

        if isinstance(args, dict):
            return record.msg, dict(args)

        if isinstance(args, tuple) and args and isinstance(args[-1], dict):
            *positional, context = args
            event = dict(context) if isinstance(context, dict) else {}
            if positional:
                event['args'] = list(positional)
            return record.msg, event

        return record.getMessage(), {}


def _getLogger(
    name:     str,
    level:    int                              = logging.CRITICAL,
    handlers: list[logging.Handler] | None     = None,
    context:  dict | None                      = None,
) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - If no handlers are provided, the logger will not output any logs.
    - This function requires the handlers to be initialized when passed as args.
    - the same log level is applied to all handlers.
    '''

    # create the root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # close/remove any existing handlers
    while logger.handlers:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

    # create the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # close/remove any existing handlers
    while logger.handlers:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

    # add the new handlers
    for handler in (handlers or []):
        logger.addHandler(handler)

    if logger.handlers:
        # only set the first handler to use the custom formatter
        logger.handlers[0].setFormatter(LogFormatter(defaults=context or {}))

    return logger

def getLogger(
    name:     str,
    level:    int                       = -1,
    stream:   TextIO                    = sys.stdout,
    files:    dict[int, str] | None     = None,
    context:  dict | None               = None,
) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - `name` is the name of the logger.
    - `stream` is the output stream for the logger (default is STDERR).
    - `files` is a dictionary of log levels and filenames for file handlers.
      - The keys are log levels (e.g., LogLevel.INFO, LogLevel.DEBUG).
      - The values are the filenames to log to at the corresponding level.
      - The file handlers will use `TimedRotatingFileHandler` to rotate logs at midnight and keep 7 backups.
    - `level` is the log level for the logger and all handlers (default is INFO).
        - if `level` is not provided, it will check the environment variable `LOG_LEVEL` and use its value if it exists
        - otherwise it defaults to `LogLevel.INFO`.
    '''

    if level == -1:
        if 'LOG_LEVEL' in os.environ:
            level = getattr(logging, os.environ['LOG_LEVEL'].upper())
        else:
            level = DEFAULT_LOG_LEVEL

    handlers: list[logging.Handler] = []
    if stream:
        handler = logging.StreamHandler(stream)
        handler.setLevel(level)
        handlers.append(handler)

    for flevel, filename in (files or {}).items():
        fhandler = TimedRotatingFileHandler(
            filename, when='midnight', backupCount=7, encoding='utf-8',
        )
        fhandler.setLevel(flevel)
        handlers.append(fhandler)

    return _getLogger(name, level, handlers, context=context)
