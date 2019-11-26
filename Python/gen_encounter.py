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
@click.option('-d','--debug_ind', default=0, help='Show all the gory details.')

def gen_encounter(party_name, hero_party_size, opponent_party_size, debug_ind):
    t = Trace_it("encounter")
    db = InvokePSQL()
    Heroes = []
    Opponents = []

    with t.tracer.span(name='root'):

        with t.tracer.span(name='heroes_setup'):
            if (party_name is not None):
                sql=f"select count(name) from dnd_5e.party where name = '{party_name}'"
                res = db.query(sql)
                hero_party_size = int(res[0][0])
                full_party = Party(db,name=party_name, debug_ind=debug_ind)
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
        print(f"Character damage info:")
        for Hero in Heroes:
            t_dict = Hero.get_damage_dealt()
            print(f"  {Hero.get_name()} attacks: {Hero.attack_success_count}/{Hero.attack_roll_count}"
                  f" nat20s:{Hero.attack_roll_nat20_count} nat1s: {Hero.attack_roll_nat1_count}")
            print(Hero.attack_rolls)
            print(f"  {Hero.get_name()} damage dealt ({t_dict['Total']}): {Hero.get_damage_dealt()}")
            t_dict = Hero.get_damage_taken()
            print(f"  {Hero.get_name()} damage taken ({t_dict['Total']}): {Hero.get_damage_taken()}")
        for Opponent in Opponents:
            t_dict = Opponent.get_damage_dealt()
            print(f"  {Opponent.get_name()} attacks: {Opponent.attack_success_count}/{Opponent.attack_roll_count}"
                  f" nat20s: {Opponent.attack_roll_nat20_count} nat1s: {Opponent.attack_roll_nat1_count}")
            print(Opponent.attack_rolls)
            print(f"  {Opponent.get_name()} damage dealt ({t_dict['Total']}): {Opponent.get_damage_dealt()}")
            t_dict = Opponent.get_damage_taken()
            print(f"  {Opponent.get_name()} damage taken ({t_dict['Total']}): {Opponent.get_damage_taken()}")

if __name__ == '__main__':
    gen_encounter()