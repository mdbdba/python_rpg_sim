from dataclasses import dataclass, field
from typing import Dict, List   # Others: Set, Tuple, Optional
from CommonFunctions import stringTostringArray
from datetime import datetime

import wrapt
import logging
import structlog

def ctx_decorator(ctx):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwds):
        ctx.fullyqualified = wrapped.__qualname__
        t = []
        if '.' in ctx.fullyqualified:
            t = stringTostringArray(ctx.fullyqualified, '.')
            t_class = t[0]
            t_method = t[1]

            print(f'SRC: class: {t_class} function: {t_method} params: {args} {kwds}')
            ctx.add_crumb(t_class,t_method, kwds)
            ret = wrapped(*args, **kwds)
            print("print attempt")
            ctx.print_crumbs()
            ctx.pop_crumb()
            return ret
        else:
            return wrapped(*args, **kwds)
    return wrapper

class rpg_logging:
    def __init__(self, logger_name='rpg_logging', level_threshold='warning'):
        switcher = {
            'notset': logging.NOTSET,
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        log_level = switcher.get(level_threshold, logging.WARNING)
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                # structlog.processors.KeyValueRenderer(sort_keys=True)
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.render_to_log_kwargs,
                structlog.processors.ExceptionPrettyPrinter(),
                #structlog.processors.JSONRenderer(indent=1, sort_keys=True),
                structlog.processors.JSONRenderer(indent=2),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer()
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = structlog.get_logger(logger_name)
        self.logger.addHandler(handler)
        self.logger.setLevel(log_level)
        self.logger.info("logger configured")

    def get_logger(self):
        return self.logger
    def get_log_rec(self, msg, ctx, return_crumbs='None'):
        crumb = []
        crumbs = []
        if (return_crumbs == 'One' or return_crumbs == 'All'):
            crumb = ctx.get_last_crumb()
        if return_crumbs == 'All':
            crumbs = ctx.get_crumbs()


        return {'_text': msg,
                'app_username': ctx.app_username,
                'study_instance_id': ctx.study_instance_id,
                'series_id': ctx.series_id,
                'encounter_id': ctx.encounter_id,
                'round': ctx.round,
                'turn': ctx.turn,
                'crumb': crumb,
                'crumbs': crumbs}

    def notset(self, msg, ctx):
        self.logger.notset(self.get_log_rec(msg,ctx))

    def debug(self, msg, ctx):
        self.logger.debug(self.get_log_rec(msg, ctx, 'All'))

    def info(self, msg, ctx):
        self.logger.info(self.get_log_rec(msg, ctx, 'One'))

    def warning(self, msg, ctx):
        self.logger.warning(self.get_log_rec(msg, ctx))

    def error(self, msg, ctx):
        self.logger.error(self.get_log_rec(msg, ctx, 'One'))

    def critical(self, msg, ctx):
        self.logger.critical(self.get_log_rec(msg, ctx, 'All'))


@dataclass
class Crumb:
    className: str
    methodName: str
    methodParams: Dict
    timestamp: datetime = datetime.now()

def init_crumbs():
    return []


@dataclass
class Ctx:
    app_username: str = "Unknown"
    fullyqualified: str = ""
    study_instance_id: int = -1
    series_id: int = -1
    encounter_id: int = -1
    round: int = 0
    turn: int = 0
    crumbs: List[Crumb] = field(default_factory=init_crumbs)

    def add_crumb(self, class_name: str, method_name: str, method_params: Dict):
        t_crumb = Crumb(class_name, method_name, method_params)
        self.crumbs.append(t_crumb)

    def pop_crumb(self):
        self.crumbs.pop()

    def print_crumbs(self):
        for crumb in self.crumbs:
            print(crumb)

    def get_last_crumb(self):
        if len(self.crumbs) > 0:
            return_value = self.crumbs[-1]
        else:
            return_value = []
        return return_value


    def get_crumbs(self):
        if len(self.crumbs) > 0:
            return_value = self.crumbs
        else:
            return_value = []
        return return_value


if __name__ == '__main__':
    ctx = Ctx(app_username='demo_user_1', encounter_id=123, round=0, turn=0)
    ctx.add_crumb('bogus_class', 'a_method', {"param1": "value1", "param2": 2})
    ctx.add_crumb('bogus_class', 'b_method', {"param1": "value3", "param2": 4})
    ctx.add_crumb('bogus_class', 'c_method', {"param1": "value5", "param2": 6})
    print(ctx.print_crumbs())
    print(ctx.get_last_crumb())
    ctx.pop_crumb()
    print(ctx.get_last_crumb())
    l = rpg_logging('ctx_main_test', 'debug')
    l.debug("debug message", ctx)
    l.info("info message", ctx)
    l.warning("warning message", ctx)
    l.error("error message", ctx)
    l.critical("critical message", ctx)
