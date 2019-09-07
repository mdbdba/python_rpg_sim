import click
from Party import Party
from InvokePSQL import InvokePSQL
from PlayerCharacter import PlayerCharacter
from Foe import Foe
from Encounter import Encounter
from Trace_it import Trace_it


@click.command()
@click.option('-p','--party_name', default=None, help='Identifier from the party table')
@click.option('-h','--hero_party_size', default=None, help='If party name is not provided, Gen randoms to this size.')
@click.option('-o','--opponent_party_size', required=True, help='Gen random foes to this size.')

def gen_encounter(party_name, hero_party_size, opponent_party_size):
    t = Trace_it("encounter")
    db = InvokePSQL()
    Heroes = []
    Opponents = []
    debug_ind = 0

    with t.tracer.span(name='root'):

        with t.tracer.span(name='heroes_setup'):
            if (party_name is not None):
                sql=f"select count(name) from dnd_5e.party where name = '{party_name}'"
                res = db.query(sql)
                hero_party_size = int(res[0][0])
                full_party = Party(db,name=party_name)
                for tmp_char in full_party.get_party():
                    Heroes.append(tmp_char)
            else:
                for hero_counter in range(hero_party_size):
                    t_label = f'hero_{hero_counter}_setup'
                    with t.tracer.span(name=t_label):
                        Heroes.append(PlayerCharacter(db, debug_ind=debug_ind))

        with t.tracer.span(name='opponents_setup'):
            for opponent_counter in range(int(opponent_party_size)):
                t_label = f'opponent_{opponent_counter}_setup'
                with t.tracer.span(name=t_label):
                    Opponents.append(Foe(db, debug_ind=debug_ind))

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

if __name__ == '__main__':
    gen_encounter()