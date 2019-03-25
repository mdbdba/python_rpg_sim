import math
# import os
# import sys
from operator import itemgetter
from fieldSector import fieldSector
from PlayerCharacter import PlayerCharacter
from Foe import Foe

from InvokePSQL import InvokePSQL


class Encounter(object):
    def __init__(self,
                 Heroes,
                 Opponents,
                 field_size=100,
                 ):
        self.Heroes = Heroes
        self.Opponents = Opponents
        self.active = True
        self.round = 0
        # initialize the field.
        self.field_map = [[fieldSector()] * field_size
                          for i in range(field_size)]
        self.field_size = field_size - 1
        self.initiative = []   # list of lists to iterate over
        sz = len(Heroes)
        for position, Hero in enumerate(Heroes):
            self.addToInitiativeArray(Hero, 'Heroes', sz, position)

        sz = len(Opponents)
        for position, Opponent in enumerate(Opponents):
            self.addToInitiativeArray(Opponent, 'Opponents', sz,
                                      position)
        self.initiative = sorted(self.initiative, reverse=True,
                                 key=itemgetter(3))
        self.masterLoop()

    def calculateDistance(self, x1, y1, x2, y2):
        dist = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)) * 5
        return dist

    def addToInitiativeArray(self, srcList, sourceArrayName, arraySize,
                             sourceArrayPosition):
        pc = srcList.Check('Perception', 'Normal', 10)
        ini = srcList.rollForInitiative('Normal')
        if sourceArrayName == 'Heroes':
            MapLocY = 1
        else:
            MapLocY = self.field_size

        if sourceArrayPosition == 0:
            MapLocX = int(self.field_size/2)
        elif sourceArrayPosition % 2 == 0:
            MapLocX = (int(self.field_size/2) + int(sourceArrayPosition / 2)
                       + (sourceArrayPosition % 2 > 0))
        else:
            MapLocX = (int(self.field_size/2) - int((sourceArrayPosition / 2)
                       + (sourceArrayPosition % 2 > 0)))

        self.field_map[MapLocX][MapLocY].occupySector()

        self.initiative.append([sourceArrayName, sourceArrayPosition,
                               pc, ini,
                               MapLocX, MapLocY])

    def masterLoop(self):
        self.round = 1
        while self.active:
            for i in range(len(self.initiative)):
                if self.initiative[i][0] == "Heroes":
                    curActive = self.Heroes[self.initiative[i][1]]
                else:
                    curActive = self.Opponents[self.initiative[i][1]]
                print(f'Round: {self.round} Turn: {i} '
                      f'Name: {curActive.getName()}')

            if self.round == 10:
                self.active = False
            self.round += 1


if __name__ == '__main__':
    db = InvokePSQL()
    Heroes = []
    Opponents = []
    Heroes.append(PlayerCharacter(db, debugInd=1))
    Opponents.append(Foe(db, foeCandidate='Skeleton', debugInd=1))
    e1 = Encounter(Heroes, Opponents)
    print(e1.initiative)
    print(f'[0,10],[0,11] {e1.calculateDistance(0,10, 0,11)} feet')
    print(f'[0,10],[99,11] {e1.calculateDistance(0,10, 99,11)} feet')
