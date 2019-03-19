from InvokePSQL import InvokePSQL
from Character import Character


class Foe(Character):
    def __init__(self,
                 db,
                 foeId=-1,
                 creatureCandidate="Random",
                 level="1",
                 debugInd=0):
        genderCandidate = 'U'
        abilityArrayStr = 'Common'
        level = 1
        Character.__init__(self, db, genderCandidate, abilityArrayStr,
                           level, debugInd)


if __name__ == '__main__':
    db = InvokePSQL()
    a1 = Foe(db, creatureCandidate="Skeleton")
