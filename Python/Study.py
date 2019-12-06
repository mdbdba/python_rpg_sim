import sys
from Ctx import Ctx, ctx_decorator, RpgLogging

ctx = Ctx(app_username='Study_class_init')


class Study:
    @ctx_decorator(ctx)
    def __init__(self, ctx: Ctx, app_username: str, study_name: str,
                 study_instance_id: int = None, repititions: int = None):
        self.ctx = ctx
        if self.ctx.app_username == "Unknown" or self.ctx.app_username == "Study_class_init":
            self.ctx.app_username = app_username

        self.log = RpgLogging(logger_name='study_logger', level_threshold='debug')
        self.app_username = app_username
        self.study_name = study_name
        self.repititions = repititions
        if study_instance_id is None:
            self.log.debug("Setting up Study Instance", self.ctx)
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

    @ctx_decorator(ctx)
    def test_method_a(self, id):
        self.log.debug("entering test method a", self.ctx)
        print(f"in test_method_a: {id}")
        self.test_method_b(id=2)

    @ctx_decorator(ctx)
    def test_method_b(self, id):
        self.log.debug("entering test method b", self.ctx)
        print(f"in test_method_b: {id}")
        self.test_method_c(id=3)

    @ctx_decorator(ctx)
    def test_method_c(self, id):
        self.log.debug("entering test method c", self.ctx)
        print(f"in test_method_c: {id}")


if __name__ == "__main__":

    study = Study(app_username='Demo_user_1', study_name='Stats Compare', ctx=ctx)
    try:
        print(ctx.get_last_crumb())
        print(ctx.print_crumbs())
        raise Exception("try/exception test")
    except Exception:
        study.log.critical("Unexpected Error Encountered", ctx)
        print(f'fallback for error stack: {sys.exc_info()}')
    else:
        print("No issues, chief.")

