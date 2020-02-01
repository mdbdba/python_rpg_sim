import random
from PointInTimeAmount import RollAmount
from Ctx import Ctx
from Ctx import ctx_decorator
from Ctx import RpgLogging


class Die(object):
    @ctx_decorator
    def __init__(self, ctx, sides=20, debug_ind=False):
        """
        Randomization class

        :param sides: the number of sides this die will have (default: 20)
        :param debug_ind: log to class_eval array? (default: False)
        """
        self.sides = sides
        self.debug_ind = debug_ind
        self.details = []  # RollAmount(die_used=sides)
        self.logger = RpgLogging(logger_name=ctx.logger_name)

    def get_last_detail(self):
        """
        Return a list of the RollAmount dataclass instances
        """
        return self.details[-1]

    def get_details(self):
        """
        Return a list of the RollAmount dataclass instances
        """
        return self.details

    # _perform_roll should only be used by the other methods. The "_" at
    # the beginning of the name is a convention Python uses for
    # that sort of thing (more info: Python private method convention)
    # This simplifies the calls being done from the other methods

    @ctx_decorator
    def _perform_roll(self, ctx, rolls, dropvalue=False,
                      dropfrom="Low", halved=False):
        """
        Handles the calculations for the class.

        :param rolls:     How many rolls to do
        :param dropvalue: Drop a value? (default: False)
        :param dropfrom:  If Dropping, from which end? (default: "Low")
        :param halved:    Cut sum in half? (default: False)

        """
        t_roll_details = RollAmount(die_used=self.sides)
        t_roll_details.die_rolls = rolls
        # print(f'adding roll id: {t_roll_details.roll_id} to {ctx.crumbs[-1]}')
        ctx.add_roll_id(t_roll_details.roll_id)
        if dropvalue:
            t_roll_details.adjustment_values["dropvalue"] = dropvalue
            t_roll_details.adjustment_values["dropfrom"] = dropfrom
        if halved:
            t_roll_details.adjustment_values["halved"] = halved

        tmp_hold = []  # list to hold all rolled values
        tot = 0       # variable to hold the total sum value

        for x in range(0, rolls):  # place the roll results in the tmpHold list
            raw_roll = random.randint(1, self.sides)
            tmp_hold.append(raw_roll)
            t_roll_details.base_roll.append(raw_roll)

        # If dropping from either side, sort the array accordingly
        if dropvalue:
            if dropfrom == "High":
                tmp_hold.sort(reverse=True)
            else:
                tmp_hold.sort()

            del tmp_hold[0]  # then remove the first value

        for y in tmp_hold:  # compute the sum of all values left
            tot = tot + y

        if halved:  # halve value rounding down (floor)
            tot = tot // 2

        t_roll_details.die_total_used = tot

        self.details.append(t_roll_details)

        # raise Exception('Test Exception')
        self.logger.debug(t_roll_details, ctx)

        return tot

    @ctx_decorator
    def roll(self, ctx, rolls=1, droplowest=False):
        """
        Perform a number of standard rolls and return the sum

        :param rolls: How many times to roll the die (Default: 1)
        :param droplowest: Drop the lowest value? (Default: False)

        """
        if droplowest:
            result = self._perform_roll(rolls=rolls, ctx=ctx, dropvalue=True, dropfrom="Low")
        else:
            result = self._perform_roll(rolls=rolls, ctx=ctx, dropvalue=False)

        return result

    @ctx_decorator
    def roll_with_advantage(self, ctx):
        """
        Perform a single roll with advantage

        """
        return self._perform_roll( ctx=ctx, rolls=2, dropvalue=True, dropfrom="Low")

    @ctx_decorator
    def roll_with_disadvantage(self, ctx):
        """
        Perform a single roll with disadvantage

        """
        return self._perform_roll(ctx=ctx, rolls=2, dropvalue=True, dropfrom="High")

    @ctx_decorator
    def roll_with_resistance(self, ctx, rolls):
        """
        Perform rolls and return half the total sum

        """
        return self._perform_roll(ctx=ctx, rolls=rolls, dropvalue=False, halved=True)

    @ctx_decorator
    def get_sum(self, ctx, startingval, multiplier):
        return startingval + self.roll(ctx=ctx, rolls=multiplier)


# Define a basic test case that'll just make sure the class works.
if __name__ == '__main__':
    ctx = Ctx(app_username='Die_init')
    d6 = Die(ctx=ctx, sides=6)
    print(f'Roll d6 3 times: {d6.roll(ctx=ctx, rolls=3, droplowest=False)}')
    print(f'Roll d6 4 times, drop lowest: {d6.roll(ctx=ctx, rolls=4, droplowest=True)}')
    print(f'Roll with advantage: {d6.roll_with_advantage(ctx=ctx)}')
    print(f'Roll with disadvantage: {d6.roll_with_disadvantage(ctx=ctx)}')
    print(f'Roll for damage with resistance: {d6.roll_with_resistance(ctx=ctx, rolls=6)}')
    print(f'get_sum: {d6.get_sum(ctx=ctx, startingval=3, multiplier=1)}')
    print(d6.get_last_detail())
    for each_roll in d6.details:
        print(each_roll)