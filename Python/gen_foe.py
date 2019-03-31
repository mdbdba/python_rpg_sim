#!/usr/bin/env python

from InvokePSQL import InvokePSQL
from Foe import Foe

db = InvokePSQL()
print("Debug info follows")
a1 = Foe(db, debugInd=1)
print("ClassEval info follows")
for i in range(len(a1.getClassEval())):
    for key, value in a1.getClassEval()[i].items():
        print(f"{i} -- {str(key).ljust(25)}: {value}")
