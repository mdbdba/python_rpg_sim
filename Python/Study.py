import sys
import traceback
import random
from InvokePSQL import InvokePSQL
from Ctx import ctx_decorator
from Ctx import Ctx
from Ctx import RpgLogging
from TraceIt import TraceIt


class Study:
    @ctx_decorator()
    def __init__(self, db, ctx: Ctx, tracer: TraceIt, app_username: str, study_name: str,
                 study_instance_id: int = None, repetitions: int = None):
        self.ctx = ctx
        self.method_last_call_audit = {}
        if self.ctx.app_username == "Unknown" or self.ctx.app_username == "Study_class_init":
            self.ctx.app_username = app_username

        self.logger = RpgLogging(logger_name=ctx.logger_name)
        self.t = tracer
        self.study_name = study_name
        self.repititions = repetitions
        if study_instance_id is None:
            # ----- TODO  ----------------
            # Get study information from db and create a new record in the study_instance table
            # Pass the context,
            self.study_instance_id = 1
            if self.ctx.study_instance_id == -1:
                self.log.debug("Updating Context for study instance id", self.ctx)
                self.ctx.study_instance_id = self.study_instance_id
        self.test_method_a(id=1)
        #

        self.log.debug("Leaving class init.", self.ctx)

    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

    @ctx_decorator()
    def test_method_a(self, id):
        self.log.debug("entering test method a", self.ctx)
        print(f"in test_method_a: {id}")
        self.test_method_b(id=2)

    @ctx_decorator()
    def test_method_b(self, id):
        self.log.debug("entering test method b", self.ctx)
        print(f"in test_method_b: {id}")
        self.test_method_c(id=3)

    @ctx_decorator()
    def test_method_c(self, id):
        self.log.debug("entering test method c", self.ctx)
        print(f"in test_method_c: {id}")


if __name__ == "__main__":
    study_id = random.randrange(0, 100000, 2)
    logger_name = f'study_main_{study_id}'
    ctx = Ctx(app_username='study_class_init', logger_name=logger_name)
    logger = RpgLogging(logger_name=logger_name, level_threshold='debug')
    logger.setup_logging()
    try:
        db = InvokePSQL()
        # series_dict = {
        #     "opponent_party_size": "4",
        #     "opponent_candidate": "Skeleton",
        #     "debug_ind": "1",
        #     "party_name": "AvgJoes_5"
        # }

        t = TraceIt("study")

        study = Study(db=db, ctx=ctx, app_username='Demo_user_1', study_name='Stats Compare', tracer=t)

    except Exception as error:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f'Context Information:\n\t'
              f'App_username:      {ctx.app_username}\n\t'
              f'Full Name:         {ctx.fully_qualified}\n\t'
              f'Logger Name:       {ctx.logger_name}\n\t'
              f'Trace Id:          {ctx.trace_id}\n\t'
              f'Study Instance Id: {ctx.study_instance_id}\n\t'
              f'Study Name:        {ctx.study_name}\n\t'
              f'Series Id:         {ctx.series_id}\n\t'
              f'Encounter Id:      {ctx.encounter_id}\n\t'
              f'Round:             {ctx.round}\n\t'
              f'Turn:              {ctx.turn}\n')

        for line in ctx.crumbs:
            print(line)

        for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
            print(line)
