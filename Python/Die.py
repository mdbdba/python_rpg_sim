import random


class Die(object):
    def __init__(self, sides=20, debug_ind=False):
        """
        Randomization class

        :param sides: the number of sides this die will have (default: 20)
        :param debug_ind: log to class_eval array? (default: False)
        """
        self.sides = sides
        self.classEval = []
        self.debug_ind = debug_ind
        self.classEval.append({"Die": sides, "debug_ind": debug_ind})
        self.callEval = {}

    def get_class_eval(self):
        """
        Return an array of lists that can be used for debugging/testing
        """
        return self.classEval

    # _perform_roll should only be used by the other methods. The "_" at
    # the beginning of the name is a convention Python uses for
    # that sort of thing (more info: Python private method convention)
    # This simplifies the calls being done from the other methods

    def _perform_roll(self, rolls, dropvalue=False,
                      dropfrom="Low", halved=False):
        """
        Handles the calculations for the class.

        :param rolls:     How many rolls to do
        :param dropvalue: Drop a value? (default: False)
        :param dropfrom:  If Dropping, from which end? (default: "Low")
        :param halved:    Cut sum in half? (default: False)

        """
        if self.debug_ind:
            self.callEval["rolls"] = rolls
            self.callEval["dropvalue"] = dropvalue
            if dropvalue:
                self.callEval["dropfrom"] = dropfrom
            self.callEval["halved"] = halved

        tmp_hold = []  # list to hold all rolled values
        tot = 0       # variable to hold the total sum value

        for x in range(0, rolls):  # place the roll results in the tmpHold list
            raw_roll = random.randint(1, self.sides)
            tmp_hold.append(raw_roll)

        # If dropping from either side, sort the array accordingly
        if dropvalue:
            if dropfrom == "High":
                tmp_hold.sort(reverse=True)
            else:
                tmp_hold.sort()

            if self.debug_ind:
                self.callEval["array_sorted"] = tmp_hold[:]

            del tmp_hold[0]  # then remove the first value

        if self.debug_ind:
            self.callEval["array"] = tmp_hold[:]

        for y in tmp_hold:  # compute the sum of all values left
            tot = tot + y

        if self.debug_ind:
            self.callEval["total"] = tot

        if halved:  # halve value rounding down (floor)
            tot = tot // 2
            if self.debug_ind:
                self.callEval["total_halved"] = tot

        return tot

    def roll(self, rolls=1, droplowest=False):
        """
        Perform a number of standard rolls and return the sum

        :param rolls: How many times to roll the die (Default: 1)
        :param droplowest: Drop the lowest value? (Default: False)

        """
        if self.debug_ind:
            self.callEval["called"] = "roll"
        if droplowest:
            result = self._perform_roll(rolls, dropvalue=True, dropfrom="Low")
        else:
            result = self._perform_roll(rolls, dropvalue=False)

        if self.debug_ind:
            self.classEval.append(self.callEval)
            self.callEval = {}

        return result

    def roll_with_advantage(self):
        """
        Perform a single roll with advantage

        """
        if self.debug_ind:
            self.callEval["called"] = "roll_with_advantage"
        retval = self._perform_roll(2, dropvalue=True, dropfrom="Low")
        if self.debug_ind:
            self.classEval.append(self.callEval)
            self.callEval = {}

        return retval

    def roll_with_disadvantage(self):
        """
        Perform a single roll with disadvantage

        """
        if self.debug_ind:
            self.callEval["called"] = "roll_with_disadvantage"
        retval = self._perform_roll(2, dropvalue=True, dropfrom="High")
        if self.debug_ind:
            self.classEval.append(self.callEval)
            self.callEval = {}

        return retval

    def roll_with_resistance(self, rolls):
        """
        Perform rolls and return half the total sum

        """
        if self.debug_ind:
            self.callEval["called"] = "roll_with_resistance"
        retval = self._perform_roll(rolls, dropvalue=False, halved=True)
        if self.debug_ind:
            self.classEval.append(self.callEval)
            self.callEval = {}
        return retval

    def get_sum(self, startingval, multiplier):
        if self.debug_ind:
            self.callEval["called"] = "get_sum"
        if self.debug_ind:
            self.classEval.append(self.callEval)
            self.callEval = {}
        return startingval + self.roll(multiplier)


# Define a basic test case that'll just make sure the class works.
if __name__ == '__main__':
    d6 = Die(6)
    print(f'Roll d6 3 times: {d6.roll(3, droplowest=False)}')
    print(f'Roll d6 4 times, drop lowest: {d6.roll(4, droplowest=True)}')
    print(f'Roll with advantage: {d6.roll_with_advantage()}')
    print(f'Roll with disadvantage: {d6.roll_with_disadvantage()}')
    print(f'Roll for damage with resistance: {d6.roll_with_resistance(6)}')
    print(f'get_sum: {d6.get_sum(3, 1)}')
    print(d6.get_class_eval()[-1])
