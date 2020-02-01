from dataclasses import dataclass, field
from typing import Dict, List   # Others: Set, Tuple, Optional
from CommonFunctions import string_to_string_array
from CommonFunctions import get_random_key
from datetime import datetime

import wrapt
import logging
import structlog
import itertools
import sys


@wrapt.decorator
def ctx_decorator(wrapped, instance, args, kwds):
    # print(f'instance: {instance}')
    ctx = kwds.get('ctx')
    ctx.fullyqualified = wrapped.__qualname__
    if '.' in ctx.fullyqualified:
        t = string_to_string_array(ctx.fullyqualified, '.')
        t_class = t[0]
        t_method = t[1]
        logger = RpgLogging(logger_name=ctx.logger_name)
        event_id = f'EV{get_random_key()}'
        start_time = datetime.now()

        # logger.debug(f'Entering {ctx.fullyqualified} event: {event_id} start_time: {start_time}', ctx)
        ctx.add_crumb(class_name=t_class, method_name=t_method, method_params=kwds, event_id=event_id)
        ret = None
        try:
            ret = wrapped(*args, **kwds)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        finally:
            end_time = datetime.now()
            logger.debug(f"Event: {event_id} Crumb: {ctx.crumbs[-1]} start_time: {start_time} " 
                         f"end_time: {end_time} returned: {ret}", ctx)
        # print("print attempt")
        # ctx.print_crumbs()
        if len(ctx.crumbs[-1].rollIds) > 0:
            if ctx.crumbs[-1].className == 'Die':
                ctx.crumbs[-2].rollIds.extend(ctx.crumbs[-1].rollIds)
            else:
                msg = (f'classname: {ctx.crumbs[-1].className} methodName: {ctx.crumbs[-1].methodName} '
                      f'used rolls: {ctx.crumbs[-1].rollIds}')
                logger.debug(msg, ctx)

        ctx.pop_crumb()
        return ret
    else:
        return wrapped(*args, **kwds)


@dataclass
class Crumb:
    className: str
    methodName: str
    methodParams: Dict
    rollIds: List
    userName: str
    event_id: str
    timestamp: datetime = datetime.now()

    def __str__(self):
        out_str = (f'class_name: {self.className}, '
                   f'method_name: {self.methodName}, '
                   'method_params: {' )
        for mhd in self.methodParams.keys():
            if mhd != 'ctx':
                out_str = (f'{out_str} {mhd}: {self.methodParams[mhd]}, ')
        out_str = (f'{out_str[:-2]}}}, roll_ids: {self.rollIds}, ' 
                   f'timestamp: {self.timestamp}')
        return out_str

    def __repr__(self):
        out_str = (f'class_name: {self.className!r}, '
                   f'method_name: {self.methodName!r}, '
                   'method_params: {' )
        for mhd in self.methodParams.keys():
            if mhd != 'ctx':
                out_str = (f'{out_str} {mhd!r}: {self.methodParams[mhd]!r}, ')
        out_str = (f'{out_str[:-2]!r}}}, roll_ids: {self.rollIds!r}, '
                   f'timestamp: {self.timestamp!r}')
        return out_str


def init_crumbs():
    return []


@dataclass
class Ctx:
    app_username: str = "Unknown"
    fullyqualified: str = ""
    logger_name: str = fullyqualified
    trace_id: str = ""
    request_type = "Standard"   # or "Trace"
    study_instance_id: int = -1
    study_name: str = ""
    series_id: int = -1
    encounter_id: int = -1
    round: int = 0
    turn: int = 0
    log_counter = itertools.count(1,1)
    crumbs: List[Crumb] = field(default_factory=init_crumbs)


    def get_next_log_id(self):
        return next(self.log_counter)

    def add_crumb(self, class_name: str, method_name: str, method_params: Dict,
                  event_id: str,  user_name: str='Unknown'):
        t_crumb = Crumb(className=class_name, methodName=method_name, methodParams=method_params,
                        rollIds=[], userName=user_name, event_id=event_id)
        self.crumbs.append(t_crumb)

    def add_roll_id(self, roll_id):
        self.crumbs[-1].rollIds.append(roll_id)

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

class RpgLogging:
    def __init__(self, logger_name='rpg_logging', level_threshold='warning'):
        switcher = {
            'notset': logging.NOTSET,
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        self.log_level = switcher.get(level_threshold, logging.WARNING)
        self.logger_name = logger_name
        self.logger = structlog.get_logger(logger_name)


    def setup_logging(self):
        logging.basicConfig(
            format="%(message)s",
            level=self.log_level,
            filename=f'../logs/{self.logger_name}.log',
            filemode='w'
        )
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.render_to_log_kwargs,
                structlog.processors.ExceptionPrettyPrinter(),
                structlog.processors.JSONRenderer(indent=2),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        formatter = structlog.stdlib.ProcessorFormatter(
            # processor=structlog.dev.ConsoleRenderer()
            processor=structlog.processors.JSONRenderer()
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = structlog.get_logger(self.logger_name)
        self.logger.addHandler(handler)
        self.logger.setLevel(self.log_level)
        self.logger.info("logger configured")

    def get_log_rec(self, msg:str, ctx:Ctx, return_crumbs='None'):
        crumb = []
        crumbs = []
        if return_crumbs == 'One' or return_crumbs == 'All':
            crumb = ctx.get_last_crumb()
        if return_crumbs == 'All':
            crumbs = ctx.get_crumbs()

        log_id = ctx.get_next_log_id()

        return {'_text': msg,
                'app_username': ctx.app_username,
                'study_name': ctx.study_name,
                'study_instance_id': ctx.study_instance_id,
                'series_id': ctx.series_id,
                'encounter_id': ctx.encounter_id,
                'trace_id': ctx.trace_id,
                'request_type':  ctx.request_type,
                'round': ctx.round,
                'turn': ctx.turn,
                'log_id': log_id,
                'crumb': crumb,
                'crumbs': crumbs}

    def notset(self, msg, ctx):
        self.logger.notset(self.get_log_rec(msg, ctx))

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



if __name__ == '__main__':
    ctx = Ctx(app_username='demo_user_1', encounter_id=123, round=0, turn=0)
    ctx.add_crumb('bogus_class', 'a_method', {"ctx": "THIS SHOULD NOT PRINT", "param1": "value1", "param2": 2}, 'EX12345')
    ctx.add_crumb('bogus_class', 'b_method', {"ctx": "THIS SHOULD NOT PRINT", "param1": "value3", "param2": 4}, 'EX23456')
    ctx.add_crumb('bogus_class', 'c_method', {"ctx": "THIS SHOULD NOT PRINT", "param1": "value5", "param2": 6}, 'EX34567')
    print(ctx.print_crumbs())
    print(ctx.get_last_crumb())
    ctx.pop_crumb()
    print(ctx.get_last_crumb())
    # -----------
    l = RpgLogging('ctx_test', 'debug')
    l.setup_logging()
    l.debug("debug message", ctx)
    l.info("info message", ctx)
    l.warning("warning message", ctx)
    l.error("error message", ctx)
    l.critical("critical message", ctx)

    m = RpgLogging('ctx_main_test', 'debug')
    m.debug("debug message", ctx)
