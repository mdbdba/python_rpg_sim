import math

from operator import itemgetter
from fieldSector import fieldSector
from PlayerCharacter import PlayerCharacter
from Foe import Foe

from InvokePSQL import InvokePSQL


class Encounter(object):
    def __init__(self,
                 Heroes,
                 Opponents,
                 field_size=100
                 ):
        self.Heroes = Heroes
        self.Opponents = Opponents
        self.active = True
        self.round = 0
        self.WinningList = ""

        # initialize the field.
        totObjs = field_size * field_size
        self.field_size = field_size
        self.field_map = [fieldSector() for x in range((totObjs))]

        self.initiative = []   # list of lists to iterate over
        self.h_cnt = len(Heroes)
        for position, Hero in enumerate(Heroes):
            self.addToInitiativeArray(Hero, 'Heroes', self.h_cnt, position)

        self.o_cnt = len(Opponents)
        for position, Opponent in enumerate(Opponents):
            self.addToInitiativeArray(Opponent, 'Opponents', self.o_cnt,
                                      position)
        self.initiative = sorted(self.initiative, reverse=True,
                                 key=itemgetter(3))
        self.masterLoop()

    def getHeroCount(self):
        return self.h_cnt

    def getOpponentCount(self):
        return self.o_cnt

    def getGridPosition(self, arrayIndex):
        return divmod(arrayIndex, (self.field_size))

    def getArrayIndex(self, x, y):
        return ((x * (self.field_size)) + y)

    def sectorIsUnoccupied(self, x, y):
        listIndex = self.getArrayIndex(x, y)
        retval = (not self.field_map[listIndex].occupied)
        print(f"Is [{x}][{y}] field_map[{listIndex}] available: {retval}")
        if (not retval):
            print(f"Occupied by: {self.field_map[listIndex].occupiedBy}"
                  f"[{self.field_map[listIndex].occupiedByIndex}]")
        return retval

    def move(self, IdentifierName, IdentifierIndex,
             leaveX, leaveY,
             occupyX, occupyY):
        leaveListInd = self.getArrayIndex(leaveX, leaveY)
        occupyListInd = self.getArrayIndex(occupyX, occupyY)
        print(f"moving {IdentifierName}[{IdentifierIndex}] from "
              f"[{leaveX}][{leaveY}] ({leaveListInd}) to "
              f"[{occupyX}][{occupyY}] ({occupyListInd})")
        self.field_map[leaveListInd].leaveSector()
        self.field_map[occupyListInd].occupySector(IdentifierName,
                                                   IdentifierIndex)

    def getTargetDistanceArray(self, myX, myY, targetName):
        distList = []
        for x in range(self.field_size * self.field_size):
            if ((self.field_map[x].occupied) and
               self.field_map[x].occupiedBy == targetName):
                a, b = self.getGridPosition(x)
                dist = self.calculateDistance(myX, myY, a, b)
                distList.append([dist, a, b, self.field_map[x].occupiedBy,
                                 self.field_map[x].occupiedByIndex])
        distList = sorted(distList, reverse=False, key=itemgetter(0))
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

        pos = self.getArrayIndex(MapLocX, MapLocY)
        self.field_map[pos].occupySector(sourceArrayName,
                                         sourceArrayPosition)

        self.initiative.append([sourceArrayName, sourceArrayPosition,
                               pc, ini,
                               MapLocX, MapLocY])

    def masterLoop(self):
        self.round = 1
        waitingFor = []
        while self.active:
            for i in range(len(self.initiative)):
                if (self.active):
                    self.Turn(i, waitingFor)
                    self.active = self.stillActive()
            if self.active:
                self.round += 1
            else:
                self.wrapUp()

    def wrapUp(self):
        print(f"The winner is: {self.WinningList} in {self.round} rounds.")


    def stillActive(self):
        retVal = False
        subVal1 = False
        subVal2 = False
        for i in range(len(self.Heroes)):
            if (self.Heroes[i].alive):
                subVal1 = True
                break
        for i in range(len(self.Opponents)):
            if (self.Opponents[i].alive):
                subVal2 = True
                break

        if (subVal1 and subVal2):
            retVal = True
        else:
            if (subVal1):
                self.WinningList = "Heroes"
            else:
                self.WinningList = "Opponents"

        return retVal

    def Turn(self, initiativeInd, waitingFor):
                if self.initiative[initiativeInd][0] == "Heroes":
                    curActive = self.Heroes[self.initiative[initiativeInd][1]]
                    targetArrayName = "Opponents"
                else:
                    curActive = (self.Opponents[
                                    self.initiative[initiativeInd][1]])
                    targetArrayName = "Heroes"

                # action_used = False
                # bonusaction_used = False

                print(f'\nRound: {self.round} Turn: {initiativeInd} '
                      f'Name: {curActive.getName()} '
                      f'Grid Pos: [{self.initiative[initiativeInd][4]}]'
                      f'[{self.initiative[initiativeInd][5]}]')

                self.removeWaitingFor(initiativeInd, waitingFor)

                dl = (self.getTargetDistanceArray(
                        self.initiative[initiativeInd][4],
                        self.initiative[initiativeInd][5],
                        targetArrayName))

                for j in range(len(dl)):
                    print(f"dist: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

                # Do they know why they are there?
                if (not self.initiative[initiativeInd][2]):
                    # bonusaction_used = True
                    self.initiative[initiativeInd][2] = (
                        curActive.Check('Perception', 'Normal', 10))
                # Move
                # Define an obj for the current active combatant
                #    0 - How many sectors can they move
                #    1 - Combat preference: 'Ranged' or 'Melee'
                #    2 - X axis location
                #    3 - Y axis location
                avail_mvmt = curActive.cur_movement / 5
                print(f"starting mvmt: {avail_mvmt} "
                      f"combat pref:   {curActive.combat_preference} "
                      f"x loc:         {self.initiative[initiativeInd][4]} "
                      f"y loc:         {self.initiative[initiativeInd][5]}")
                avail_mvmt = self.Movement(avail_mvmt,
                                           curActive,
                                           self.initiative[initiativeInd],
                                           dl)
                print(f"movement left: {avail_mvmt} "
                      f"combat pref:   {curActive.combat_preference} "
                      f"x loc:         {self.initiative[initiativeInd][4]} "
                      f"y loc:         {self.initiative[initiativeInd][5]}")

                for j in range(len(dl)):
                    print(f"dist AFTER: {dl[j][0]} {dl[j][1]} {dl[j][2]}")

                # Action (Bonus or standard)
                # If they don't have a ranged weapon or spell attack
                # they must be a melee fighter.  When not in melee range
                # use action for movement.
                curAction = curActive.getAction(dl)
                if (curAction == 'Movement'):
                    print(f"Using {curActive.getName()}'s Action for "
                          f"movement.")
                    avail_mvmt = curActive.cur_movement / 5
                    avail_mvmt = self.Movement(avail_mvmt,
                                               curActive,
                                               self.initiative[
                                                  initiativeInd],
                                               dl)
                    for j in range(len(dl)):
                        print(f"dist AFTER Action: {dl[j][0]} {dl[j][1]} "
                              f"{dl[j][2]}")
                elif (curAction == 'Wait on Melee'):
                    # If an enemy gets into melee range this round, ATTACK!
                    print(f"Using {curActive.getName()}'s Action waiting "
                          f"for an enemy to get into melee range.")
                    print(f"adding to the waiting list: "
                          f"{dl[0][3]}[{dl[0][4]}]")
                    waitingFor.append([self.initiative[initiativeInd][0],
                                       initiativeInd, dl[0][3], dl[0][4]])
                elif (curAction == 'Melee'):
                    print(f"{curActive.getName()} is in melee with "
                          f"{dl[0][3]}[{dl[0][4]}]")
                    # do any superceding actions
                    s1 = self.getWaitingFor(initiativeInd, waitingFor)
                    for waitingAction in s1:
                        # Melee action happens here.
                        print(f"{waitingAction[0]}[{waitingAction[1]}] "
                              f"has been waiting for this!")
                        if waitingAction[0] == "Heroes":
                            directedUser = self.Heroes[waitingAction[1]]
                        else:
                            directedUser = (self.Opponents[waitingAction[1]])

                        if (directedUser.alive):
                            curActive.alive = False
                            curActive.cur_hit_points = 0

                    if (curActive.cur_hit_points > 0):
                        if (dl[0][3] == "Heroes"):
                            target = self.Heroes[dl[0][4]]
                        else:
                            target = self.Opponents[dl[0][4]]

                        target.alive = False
                        target.cur_hit_points = 0

                print(f"Closest To: {dl[0][0]} {dl[0][1]} {dl[0][2]}")

    def removeWaitingFor(self, initiativeInd, waitingFor):
        print(f"Clear any waits for {self.initiative[initiativeInd][0]}"
              f"[{self.initiative[initiativeInd][1]}]")
        for sublist in waitingFor:
            if (sublist[0] == self.initiative[initiativeInd][0]
                    and sublist[1] == self.initiative[initiativeInd][1]):
                print(f"removing: {sublist[0]}[{sublist[1]}]")
                waitingFor.remove(sublist)

    def getWaitingFor(self, initiativeInd, waitingFor):
        print(f"Anyone waiting on {self.initiative[initiativeInd][0]}"
              f"[{self.initiative[initiativeInd][1]}]?")
        retVal = []
        for sublist in waitingFor:
            if (sublist[2] == self.initiative[initiativeInd][0]
                    and sublist[3] == self.initiative[initiativeInd][1]):
                retVal.append([sublist[0], sublist[1]])
                print(f"Yes: {sublist[0]}[{sublist[1]}]")
                waitingFor.remove(sublist)

        return retVal

    def Movement(self, avail_mvmt, curActive, curInit, destList):
        if (curInit[2]):     # if they've figured out what's going on.
            if (curActive.combat_preference == 'Melee'):
                # run straight towards closest enemy
                # set destination x and y
                destX = int(destList[0][1])
                destY = int(destList[0][2])
                curX = int(curInit[4])
                curY = int(curInit[5])

                print(f"Tracking: {destList[0][3]}[{destList[0][4]}]")

                if (avail_mvmt > 0) and (destList[0][0] > 5):
                    mvmt = True
                else:
                    mvmt = False

                while (mvmt):
                    distX = destX - curX
                    dirX = 1 if (distX >= 0) else -1
                    absDistX = abs(distX)

                    distY = destY - curY
                    dirY = 1 if (distY >= 0) else -1
                    absDistY = abs(distY)

                    if (distX == 0 and distY == 0):
                        print(f"distX and distY = 0. Somethings wrong.")
                        mvmt = False
                    elif (absDistX == 1 or absDistY == 1):
                        print(f"*** Is in melee with "
                              f"{destList[0][3]}[{destList[0][4]}].")
                        mvmt = False
                    elif (absDistX > absDistY):
                        prefAngAxis = 'Y'
                        prefAngDist = distY
                    else:
                        prefAngAxis = 'X'
                        prefAngDist = distX

                    if (mvmt):
                        tlX = [-1, -1, -1]
                        tlY = [-1, -1, -1]
                        if (prefAngDist == 0):
                            if (prefAngAxis == 'X'):
                                tlX[0] = curX
                                tlX[1] = curX + 1
                                tlX[2] = curX - 1
                                tlY[0] = curY + dirY
                                tlY[1] = curY + dirY
                                tlY[2] = curY + dirY
                            else:
                                tlX[0] = curX + dirX
                                tlX[1] = curX + dirX
                                tlX[2] = curX + dirX
                                tlY[0] = curY
                                tlY[1] = curY + 1
                                tlY[2] = curY - 1
                        else:
                            tmpX = curX + dirX
                            tmpY = curY + dirY
                            if (prefAngAxis == 'X'):
                                tlX[0] = tmpX
                                tlX[1] = curX
                                tlX[2] = tmpX
                                tlY[0] = tmpY
                                tlY[1] = tmpY
                                tlY[2] = curY
                            else:
                                tlX[0] = tmpX
                                tlX[1] = tmpX
                                tlX[2] = curX
                                tlY[0] = tmpY
                                tlY[1] = curY
                                tlY[2] = tmpY

                        move_success = False
                        for i in range(3):
                            if (self.sectorIsUnoccupied(tlX[i], tlY[i])):
                                self.move(curInit[0], curInit[1],
                                          curX, curY,
                                          tlX[i], tlY[i])
                                curX = tlX[i]
                                curY = tlY[i]
                                avail_mvmt -= 1
                                mvmt = False if (avail_mvmt == 0) else True
                                destList[0][0] = self.calculateDistance(
                                                    curX, curY, destX, destY)
                                move_success = True
                                break

                        if (move_success):
                            curInit[4] = curX
                            curInit[5] = curY
                        else:
                            mvmt = False

        return avail_mvmt


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

#     print(f'[0,10],[0,11] {e1.calculateDistance(0,10, 0,11)} feet')
#     print(f'[0,10],[99,11] {e1.calculateDistance(0,10, 99,11)} feet')
