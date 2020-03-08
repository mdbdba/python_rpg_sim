from dataclasses import dataclass, field
from typing import Dict, List   # Others: Set, Tuple, Optional
from CommonFunctions import string_to_string_array
from CommonFunctions import get_random_key
from CommonFunctions import fix_dict_for_json
from datetime import datetime

import wrapt
import logging
import structlog
import itertools
import sys
import traceback
import os


@wrapt.decorator
def ctx_decorator(wrapped, instance, args, kwds):
    ctx = None
    if instance and (getattr(instance, 'ctx', 'NotThere') != 'NotThere'):
        ctx = instance.ctx

    elif 'ctx' in kwds:
        ctx = kwds.get('ctx')
    if ctx is None:
        raise ValueError('ctx obj not found.')

    ctx.fullyqualified = wrapped.__qualname__
    if '.' in ctx.fullyqualified:
        username_to_use = None
        t = string_to_string_array(ctx.fullyqualified, '.')
        t_class = t[0]
        t_method = t[1]
        if t_class in ['PlayerCharacter', 'Foe', 'Character'] and t_method not in ['__init__']:
            if instance.get_name() not in ['Generic Character', 'Not Assigned']:
                username_to_use = instance.get_name()
        logger = RpgLogging(logger_name=ctx.logger_name)
        event_id = f'EV{get_random_key()}'
        start_time = datetime.now()
        if len(ctx.crumbs) == 0:
            tmp_parent_id = 0
        else:
            tmp_parent_id = ctx.crumbs[-1].event_id

        ctx.add_crumb(class_name=t_class, method_name=t_method, method_params=kwds,
                      parent_id=tmp_parent_id, event_id=event_id, user_name=username_to_use)
        ret = None
        roll_ids = {}
        try:
            ret = wrapped(*args, **kwds)
            if len(ctx.crumbs[-1].rollIds) > 0:
                if ctx.crumbs[-1].className == 'Die' and len(ctx.crumbs) > 1:
                    ctx.crumbs[-2].rollIds.extend(ctx.crumbs[-1].rollIds)
                else:
                    roll_ids = {'used rolls': ctx.crumbs[-1].rollIds}

        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        finally:
            end_time = datetime.now()
            jdict = {'Parent': tmp_parent_id,
                     'Event': event_id,
                     'start_time': str(start_time),
                     'end_time': str(end_time),
                     'duration': str(end_time - start_time),
                     'returned': str(ret)}
            if len(roll_ids) > 0:
                jdict['roll_ids'] = roll_ids
            logger.debug(msg='event_context_record', json_dict=jdict, ctx=ctx)
            try:
                instance.add_method_last_call_audit({**ctx.crumbs[-1].__dict__, **jdict})
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()

                edict = {"className": ctx.crumbs[-1].className,
                         "methodName": ctx.crumbs[-1].methodName,
                         "error": traceback.format_exception(exc_type, exc_value, exc_traceback)}
                logger.warning(msg='method_last_call_audit_error', json_dict=edict, ctx=ctx)

        ctx.pop_crumb()
        return ret
    else:
        return wrapped(*args, **kwds)


def get_hide_arg_list():
    return ['db', 'ctx', 'tracer']


def init_audit_json():
    return {}


@dataclass
class Crumb:
    className: str
    methodName: str
    methodParams: Dict
    rollIds: List
    userName: str
    parent_id: str
    event_id: str
    call_depth: int
    audit_json: Dict = field(default_factory=init_audit_json)
    timestamp: datetime = datetime.now()
    # hide_arg_list: List = field(default_factory=set_hide_arg_list)

    def add_audit(self, json_dict: Dict):
        self.audit_json = {**self.audit_json, **json_dict}

    def __str__(self):
        out_str = (f'class_name = {self.className}, '
                   f'method_name = {self.methodName}, '
                   f'userName = {self.userName}, '
                   f'parent_id =  {self.parent_id}, '
                   f'event_id =  {self.event_id}, '
                   f'call_depth =  {self.call_depth}, '
                   'method_params = {')
        for mhd in self.methodParams.keys():
            if mhd not in get_hide_arg_list():
                if isinstance(self.methodParams[mhd], (str, bool)):
                    out_str = f'{out_str} {mhd} = \'{self.methodParams[mhd]}\', '
                else:
                    out_str = f'{out_str} {mhd} = {self.methodParams[mhd]}, '
        if out_str[-2:] == ', ':
            out_str = f'{out_str[:-2]}'

        out_str = f'{out_str}}}, roll_ids = {self.rollIds}, timestamp = {str(self.timestamp)}'
        return out_str

    def __repr__(self):
        out_str = (f'{{"class_name": "{self.className}", '
                   f'"method_name": "{self.methodName}", '
                   f'"userName": "{self.userName}", '
                   f'"parent_id": "{self.parent_id}", '
                   f'"event_id": "{self.event_id}", '
                   f'"call_depth":  {self.call_depth}, '
                   '"method_params": {')
        for mhd in self.methodParams.keys():
            if mhd not in get_hide_arg_list():
                if self.methodParams[mhd] is None:
                    out_str = f'{out_str} "{mhd}": "None", '
                elif isinstance(self.methodParams[mhd], (str, bool)):
                    out_str = f'{out_str} "{mhd}": "{self.methodParams[mhd]}", '
                else:
                    out_str = f'{out_str} "{mhd}": {self.methodParams[mhd]!r}, '
        if out_str[-2:] == ', ':
            out_str = out_str[:-2]
        out_str = f'{out_str}}}, "roll_ids": {self.rollIds}, "timestamp": "{str(self.timestamp)}"}}'
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
    log_counter = itertools.count(1, 1)
    crumbs: List[Crumb] = field(default_factory=init_crumbs)

    def inc_round(self):
        self.round += 1

    def reset_turn(self):
        self.turn = 0

    def inc_turn(self):
        self.turn += 1

    def get_next_log_id(self):
        return next(self.log_counter)

    def add_crumb(self, class_name: str, method_name: str, method_params: Dict, parent_id: str,
                  event_id: str,  user_name: str = 'Unknown'):
        t_crumb = Crumb(className=class_name, methodName=method_name, methodParams=method_params,
                        rollIds=[], userName=user_name, parent_id=parent_id, event_id=event_id,
                        call_depth=(len(self.crumbs) + 1))
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
            return_value = fix_dict_for_json(self.crumbs[-1].__dict__)
        else:
            return_value = []
        return return_value

    def get_crumbs(self):
        return_value = []
        if len(self.crumbs) > 0:
            for crumb in self.crumbs:
                return_value.append(fix_dict_for_json(crumb.__dict__))
        return return_value

    def __repr__(self):
        # out_str = (f'{{ "app_username": "{self.app_username}", '
        #            f'"fullyqualified": "{self.fullyqualified}", '
        #            f'"logger_name": "{self.logger_name}", '
        #            f'"trace_id": "{self.trace_id}", '
        #            f'"request_type": "{self.request_type}", '
        #            f'"study_instance_id": "{self.study_instance_id}", '
        #            f'"study_name": "{self.study_name}", '
        #            f'"series_id": "{self.series_id}", '
        #            f'"encounter_id": "{self.encounter_id}", '
        #            f'"round": "{self.round}", '
        #            f'"turn": "{self.turn}", '
        #            f'"crumbs": [{self.crumbs}] }}')

        # return out_str
        return 'Ctx'


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
        self.round_summary_name = f"{logger_name}_round_summary"
        self.round_summary = logging.getLogger(self.round_summary_name)
        # self.field_snap_name = f"{logger_name}_field_snap"
        # self.field_snap = logging.getLogger(self.field_snap_name)

    def setup_logging(self):
        self.logger = structlog.get_logger(self.logger_name)
        self.round_summary = logging.getLogger(self.round_summary_name)
        # self.field_snap = logging.getLogger(self.field_snap_name)
        base_path = os.path.expanduser('~/rpg/logs')
        logging.basicConfig(
        # self.logger.basicConfig(
            format="%(message)s",
            level=self.log_level,
            filename=f'{base_path}/{self.logger_name}.log',
            filemode='w'
        )
        structlog.configure(
            processors=[
                # structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.render_to_log_kwargs,
                # structlog.processors.ExceptionPrettyPrinter(),
                structlog.processors.JSONRenderer(indent=4),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        summary_handler = logging.FileHandler(filename=f'{base_path}/{self.round_summary_name}.log', mode='w')
        summary_format = logging.Formatter( '%(message)s')
        summary_handler.setFormatter(summary_format)

        self.round_summary.addHandler(summary_handler)

        # field_handler = logging.FileHandler(filename=f'{base_path}/{self.field_snap_name}.log', mode='w')
        # field_format = logging.Formatter( '%(message)s')
        # field_handler.setFormatter(field_format)

        # self.field_snap.addHandler(field_handler)
        # formatter = structlog.stdlib.ProcessorFormatter(
        #     # processor=structlog.dev.ConsoleRenderer()
        #     processor=structlog.processors.JSONRenderer()
        # )
        # handler = logging.StreamHandler(sys.stdout)
        # handler.setFormatter(formatter)
        #####   self.logger = structlog.get_logger(self.logger_name)
        # self.logger.addHandler(handler)
        self.logger.setLevel(self.log_level)
        self.round_summary.setLevel(logging.INFO)
        # self.field_snap.setLevel(logging.INFO)
        # self.logger.info("logger configured")

    def get_log_rec(self, ctx: Ctx, msg: str = None, json_dict: Dict = None, return_crumbs='None'):
        if msg is None and json_dict is None:
            raise ValueError("Either msg or json_dict is required.")
        crumb = []
        crumbs = []
        if return_crumbs == 'One' or return_crumbs == 'All':
            crumb = ctx.get_last_crumb()
        if return_crumbs == 'All':
            crumbs = ctx.get_crumbs()

        log_id = ctx.get_next_log_id()
        tmp_dict = {
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
        if msg is not None:
            tmp_dict['_text'] = msg

        if json_dict is not None and len(json_dict) > 0:
            tmp_dict['_json'] = json_dict
        #     return_dict = { **tmp_dict, **json_dict}
        # else:
        #     return_dict = tmp_dict

        return tmp_dict

    def summary_entry(self, msg):
        self.round_summary.info(msg)

    # def field_snap(self, msg):
    #     print(msg)
    #     #self.field_snap.info(msg)

    def notset(self, ctx, msg=None, json_dict=None):
        self.logger.notset(self.get_log_rec(msg=msg, json_dict=json_dict, ctx=ctx))

    def debug(self, ctx, msg=None, json_dict=None):
        self.logger.debug(self.get_log_rec(msg=msg, json_dict=json_dict, ctx=ctx, return_crumbs='One'))

    def info(self, ctx, msg=None, json_dict=None):
        self.logger.info(self.get_log_rec(msg=msg, json_dict=json_dict, ctx=ctx, return_crumbs='One'))

    def warning(self, ctx, msg=None, json_dict=None):
        self.logger.warning(self.get_log_rec(msg=msg, json_dict=json_dict, ctx=ctx))

    def error(self, ctx, msg=None, json_dict=None):
        self.logger.error(self.get_log_rec(msg=msg, json_dict=json_dict, ctx=ctx, return_crumbs='One'))

    def critical(self, ctx, msg=None, json_dict=None):
        self.logger.critical(self.get_log_rec(msg=msg, json_dict=json_dict, ctx=ctx, return_crumbs='All'))


if __name__ == '__main__':
    ctx = Ctx(app_username='demo_user_1', encounter_id=123, round=0, turn=0)
    ctx.add_crumb('bogus_class', 'a_method', {"ctx": ctx, "param1": "value1", "param2": 2}, 'PA1543', 'EX12345')
    ctx.add_crumb('bogus_class', 'b_method', {"ctx": ctx, "param1": "value3", "param2": 4}, 'PA7654', 'EX23456')
    ctx.add_crumb('bogus_class', 'c_method', {"ctx": ctx, "param1": "value5", "param2": 6}, 'PA0987', 'EX34567')
    print(ctx.print_crumbs())
    print(ctx.get_last_crumb())
    ctx.pop_crumb()
    print(ctx.get_last_crumb())
    # -----------
    l = RpgLogging('ctx_test', 'debug')
    l.setup_logging()
    l.debug(msg="debug message", ctx=ctx)
    l.info(msg="info message", ctx=ctx)
    l.warning(msg="warning message", ctx=ctx)
    l.error(msg="error message", ctx=ctx)
    l.critical(msg="critical message", ctx=ctx)

    m = RpgLogging('ctx_main_test', 'debug')
    m.debug(msg="debug message", ctx=ctx)
