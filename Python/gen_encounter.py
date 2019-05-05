from InvokePSQL import InvokePSQL
from PlayerCharacter import PlayerCharacter
from Foe import Foe
from Encounter import Encounter

db = InvokePSQL()
Heroes = []
Opponents = []
Heroes.append(PlayerCharacter(db, debug_ind=1))
Heroes.append(PlayerCharacter(db, debug_ind=1))
Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=1))
Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=1))
Opponents.append(Foe(db, foe_candidate='Skeleton', debug_ind=1))
e1 = Encounter(Heroes, Opponents, debug_ind=1)
print(f"The winning party was: {e1.winning_list_name} in {e1.round} rounds.")
print(f"The surviving {e1.winning_list_name} members:")
for i in range(len(e1.winning_list)):
    if e1.winning_list[i].alive:
        print(f'{e1.winning_list[i].get_name()}')