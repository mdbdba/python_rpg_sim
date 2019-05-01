#!/usr/bin/env python

from InvokePSQL import InvokePSQL
from Foe import Foe

db = InvokePSQL()
print("Debug info follows")
a1 = Foe(db, debug_ind=1)
print("ClassEval info follows")
for i in range(len(a1.get_class_eval())):
    for key, value in a1.get_class_eval()[i].items():
        print(f"{i} -- {str(key).ljust(25)}: {value}")
