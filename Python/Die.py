import random


class Die(object):
    def __init__(self, sides=20, debugInd=False):
        """
        Randomization class

        :param sides: the number of sides this die will have (default: 20)
        :param debugInd: log to class_eval array? (default: False)
        """
        self.sides = sides
        self.classEval = []
        self.debugInd = debugInd
        self.classEval.append({"Die": sides, "debug_ind": debugInd})
        self.callEval = {}

    def getClassEval(self):
        """
        Return an array of lists that can be used for debugging/testing
        """
        return self.classEval

    # _performRoll should only be used by the other methods. The "_" at
    # the beginning of the name is a convention Python uses for
    # that sort of thing (more info: Python private method convention)
    # This simplifies the calls being done from the other methods

    def _performRoll(self, rolls, dropvalue=False,
                     dropfrom="Low", halved=False):
        """
        Handles the calculations for the class.

        :param rolls:     How many rolls to do
        :param dropvalue: Drop a value? (default: False)
        :param dropfrom:  If Dropping, from which end? (default: "Low")
        :param halved:    Cut sum in half? (default: False)

        """
        if self.debugInd:
            self.callEval["rolls"] = rolls
            self.callEval["dropvalue"] = dropvalue
            if dropvalue:
                self.callEval["dropfrom"] = dropfrom
            self.callEval["halved"] = halved

        tmpHold = []  # list to hold all rolled values
        tot = 0       # variable to hold the total sum value

        for x in range(0, rolls):  # place the roll results in the tmpHold list
            raw_roll = random.randint(1, self.sides)
            tmpHold.append(raw_roll)

        # If dropping from either side, sort the array accordingly
        if dropvalue:
            if dropfrom == "High":
                tmpHold.sort(reverse=True)
            else:
                tmpHold.sort()

            if self.debugInd:
                self.callEval["array_sorted"] = tmpHold[:]

            del tmpHold[0]  # then remove the first value

        if self.debugInd:
            self.callEval["array"] = tmpHold[:]

        for y in tmpHold:  # compute the sum of all values left
            tot = tot + y

        if self.debugInd:
            self.callEval["total"] = tot

        if halved:  # halve value rounding down (floor)
            tot = tot // 2
            if self.debugInd:
                self.callEval["total_halved"] = tot

        return tot

    def roll(self, rolls=1, droplowest=False):
        """
        Perform a number of standard rolls and return the sum

        :param rolls: How many times to roll the die (Default: 1)
        :param droplowest: Drop the lowest value? (Default: False)

        """
        if self.debugInd:
            self.callEval["called"] = "roll"
        if droplowest:
            result = self._performRoll(rolls, dropvalue=True, dropfrom="Low")
        else:
            result = self._performRoll(rolls, dropvalue=False)

        if self.debugInd:
            self.classEval.append(self.callEval)
            self.callEval = {}

        return result

    def rollWithAdvantage(self):
        """
        Perform a single roll with advantage

        """
        if self.debugInd:
            self.callEval["called"] = "rollWithAdvantage"
        retval = self._performRoll(2, dropvalue=True, dropfrom="Low")
        if self.debugInd:
            self.classEval.append(self.callEval)
            self.callEval = {}

        return retval

    def rollWithDisadvantage(self):
        """
        Perform a single roll with disadvantage

        """
        if self.debugInd:
            self.callEval["called"] = "rollWithDisadvantage"
        retval = self._performRoll(2, dropvalue=True, dropfrom="High")
        if self.debugInd:
            self.classEval.append(self.callEval)
            self.callEval = {}

        return retval

    def rollWithResistance(self, rolls):
        """
        Perform rolls and return half the total sum

        """
        if self.debugInd:
            self.callEval["called"] = "rollWithResistance"
        retval = self._performRoll(rolls, dropvalue=False, halved=True)
        if self.debugInd:
            self.classEval.append(self.callEval)
            self.callEval = {}
        return retval

    def getSum(self, startingval, multiplier):
        if self.debugInd:
            self.callEval["called"] = "getSum"
        if self.debugInd:
            self.classEval.append(self.callEval)
            self.callEval = {}
        return (startingval + self.roll(multiplier))


# Define a basic test case that'll just make sure the class works.
if __name__ == '__main__':
    d6 = Die(6)
    print(f'Roll d6 3 times: {d6.roll(3, droplowest=False)}')
    print(f'Roll d6 4 times, drop lowest: {d6.roll(4, droplowest=True)}')
    print(f'Roll with advantage: {d6.rollWithAdvantage()}')
    print(f'Roll with disadvantage: {d6.rollWithDisadvantage()}')
    print(f'Roll for damage with resistance: {d6.rollWithResistance(6)}')
    print(f'getSum: {d6.getSum(3,1)}')
    print(d6.getClassEval()[-1])
