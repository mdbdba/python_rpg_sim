from Study import Study, ctx
import sys
import click


@click.command()
@click.option('-s', '--study_name', default=None, help='Name of the study to run')
@click.option('-u', '--app_username', default=None, help='The name of the user running the sim')
def gen_study(app_username, study_name):
    ctx.add_crumb('gen_study', 'main', sys.argv)
    print(ctx)
    study = Study(app_username=app_username, study_name=study_name, ctx=ctx)
    try:
        print(ctx.get_last_crumb())
        print(ctx.print_crumbs())
    except Exception:
        study.log.critical("Unexpected Error Encountered", ctx)
        print(f'fallback for error stack: {sys.exc_info()}')
    else:
        print("No issues, chief.")


if __name__ == '__main__':
    gen_study()
