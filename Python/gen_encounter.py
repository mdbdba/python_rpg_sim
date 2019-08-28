from InvokePSQL import InvokePSQL
from PlayerCharacter import PlayerCharacter
from Foe import Foe
from Encounter import Encounter
from Trace_it import Trace_it


t = Trace_it("encounter")

with t.tracer.span(name='root'):

    db = InvokePSQL()
    Heroes = []
    Opponents = []
    debug_ind = 0
    with t.tracer.span(name='heroes_setup'):
        with t.tracer.span(name='hero_1_setup'):
            Heroes.append(PlayerCharacter(db, debug_ind=debug_ind))
        with t.tracer.span(name='hero_2_setup'):
            Heroes.append(PlayerCharacter(db, debug_ind=debug_ind))
    with t.tracer.span(name='opponents_setup'):
        with t.tracer.span(name='opponent_1_setup'):
            Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=debug_ind))
        with t.tracer.span(name='opponent_2_setup'):
            Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=debug_ind))
        with t.tracer.span(name='opponent_3_setup'):
            Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=debug_ind))
    print(f"For the Heroes:")
    for Hero in Heroes:
        print(f"  {Hero.get_name()}")
    print(f"Against:")
    for Opponent in Opponents:
        print(f"  {Opponent.get_name()}")
    e1 = Encounter(Heroes, Opponents, debug_ind=debug_ind, tracer=t.tracer)
    print(f"The winning party was: {e1.winning_list_name} in {e1.round} rounds.")
    print(f"The surviving {e1.winning_list_name} members:")
    for i in range(len(e1.winning_list)):
        if e1.winning_list[i].alive:
            print(f'{e1.winning_list[i].get_name()}')
