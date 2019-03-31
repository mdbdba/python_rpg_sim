#!/usr/bin/env python
# gen_battlefield.py

from InvokePSQL import InvokePSQL
from PlayerCharacter import PlayerCharacter
from Foe import Foe
from Encounter import Encounter

db = InvokePSQL()

Heroes = []
Opponents = []
for i in range(3):
    Heroes.append(PlayerCharacter(db, debugInd=0))
for i in range(2):
    Opponents.append(Foe(db, foeCandidate='Skeleton', debugInd=0))
e1 = Encounter(Heroes, Opponents)
# print(e1.initiative)
print("Initiative List:")
for i in e1.initiative:
    print(f'srclist: {i[0]}[{i[1]}] perc: {i[2]} ini: {i[3]} mapx: {i[4]} '
          f'mapy: {i[5]}')
print("Occupied field Sectors:")
for x in range(e1.field_size * e1.field_size):
    if (e1.field_map[x].occupied):
        a, b = e1.getGridPosition(x)
        print(f"list position:[{x}] Grid location: [{a}][{b}] "
              f"Occupied by: {e1.field_map[x].occupiedBy}"
              f"[{e1.field_map[x].occupiedByIndex}]")
