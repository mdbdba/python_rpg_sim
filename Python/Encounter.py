import math
# import numpy
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
        # row = [fieldSector()] * field_size
        # self.field_map = [list(row) for i in range(field_size)]
        # self.field_map = numpy.full((field_size, field_size), fieldSector())
        totObjs = field_size * field_size
        self.field_map = [fieldSector() for x in range((totObjs))]

        # self.field_size = field_size - 1
        self.field_size = field_size
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

#    def getDistanceBetween(self, srcLocX, srcLocY):

    def getGridPosition(self, arrayIndex):
        return divmod(arrayIndex, (self.field_size))

    def getArrayIndex(self, x, y):
        return ((x * (self.field_size)) + y)

    def getTargetDistanceArray(self, myX, myY, targetName):
        distList = []
        for x in range(self.field_size * self.field_size):
            if ((self.field_map[x].occupied) and
                self.field_map[x].occupiedBy == targetName):
                a, b = self.getGridPosition(x)
                dist = self.calculateDistance(myX, myY, a, b)
                distList.append([dist, self.field_map[x].occupiedBy,
                                 self.field_map[x].occupiedByIndex])
        return distList

    def calculateDistance(self, x1, y1, x2, y2):
        dist = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)) * 5
        return dist

    def addToInitiativeArray(self, srcList, sourceArrayName, arraySize,
                             sourceArrayPosition):
        pc = srcList.Check('Perception', 'Normal', 10)
        ini = srcList.rollForInitiative('Normal')
        field_max = self.field_size - 1

        if sourceArrayName == 'Heroes':
            MapLocX = 1
        else:
            MapLocX = field_max

        if sourceArrayPosition == 0:
            MapLocY = int(field_max/2)
        elif sourceArrayPosition % 2 == 0:
            MapLocY = (int(field_max/2) + int(sourceArrayPosition / 2)
                       + (sourceArrayPosition % 2 > 0))
        else:
            MapLocY = (int(field_max/2) - int((sourceArrayPosition / 2)
                       + (sourceArrayPosition % 2 > 0)))

        # print(f"{sourceArrayName}[{sourceArrayPosition}] "
        #       f"Occupying [{MapLocX}][{MapLocY}]")

        pos = self.getArrayIndex(MapLocX, MapLocY)
        self.field_map[pos].occupySector(sourceArrayName,
                                         sourceArrayPosition)

        self.initiative.append([sourceArrayName, sourceArrayPosition,
                               pc, ini,
                               MapLocX, MapLocY])

    def masterLoop(self):
        self.round = 1
        while self.active:
            for i in range(len(self.initiative)):
                if self.initiative[i][0] == "Heroes":
                    curActive = self.Heroes[self.initiative[i][1]]
                    targetArrayName = "Opponents"
                else:
                    curActive = self.Opponents[self.initiative[i][1]]
                    targetArrayName = "Heroes"

                print(f'Round: {self.round} Turn: {i} '
                      f'Name: {curActive.getName()}')
                dl = (self.getTargetDistanceArray(self.initiative[i][4],
                                                  self.initiative[i][5],
                                                  targetArrayName))
                for j in range(len(dl)):
                    print(f"dist: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

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
    for x in range(e1.field_size * e1.field_size):
        if (e1.field_map[x].occupied):
            a, b = e1.getGridPosition(x)
            print(f"[{x}] [{a}][{b}] {e1.field_map[x].occupiedBy}"
                  f"[{e1.field_map[x].occupiedByIndex}]")

    print(f'[0,10],[0,11] {e1.calculateDistance(0,10, 0,11)} feet')
    print(f'[0,10],[99,11] {e1.calculateDistance(0,10, 99,11)} feet')
