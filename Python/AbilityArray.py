from Die import Die
# from CommonFunctions import array_to_string, string_to_array
from CommonFunctions import string_to_array
from CommonFunctions import print_method_last_call_audit
from Ctx import Ctx
from Ctx import ctx_decorator


"""
Class for generating Ability Arrays.
Parameters:
    array_type describes how we want the array created
    choices are:
        Common  (Default) -- roll 4d6 and drop the lowest.
        Strict            -- roll 3d6. Keep the numbers as is.
        standard          -- [15, 14, 13, 12, 10, 8]
        point_buy_even        [13, 13, 13, 12, 12 ,12]
        point_buy_one_max   -- [15, 12, 12, 12, 11, 11]
        point_buy_two_max   -- [15, 15, 11, 10, 10, 10]
        point_buy_three_max -- [15, 15, 15, 8, 8, 8]
"""


class AbilityArray(object):
    @ctx_decorator
    def __init__(self, ctx: Ctx, array_type="Common",
                 raw_array=None,
                 pref_array=None,
                 racial_array=None,
                 ignore_racial_bonus=False):
        """
        Generate a list of values to serve as Ability Scores

        :param ctx: pass the context object for logging
        :param raw_array: if an array already exists treat it as is.
        :param pref_array: Array that defines how the rolls should be ordered.
        :param racial_array: Array of racial bonuses for the abilities
        :param ignore_racial_bonus: Ignore ability bonuses for races.
        """
        self.ctx = ctx
        self.method_last_call_audit = {}
        self.array_type = array_type
        self.pref_array = pref_array
        self.pref_str_array = ['', '', '', '', '', '']
        self.racial_array = racial_array
        self.ignore_racial_bonus = ignore_racial_bonus
        self.raw_array = raw_array
        self.candidate_array = []
        self.numerical_sorted_array = []
        self.pref_sorted_array = []
        self.ability_array = [0, 0, 0, 0, 0, 0]
        self.ability_imp_array = [0, 0, 0, 0, 0, 0]
        self.const_array_standard = [15, 14, 13, 12, 10, 8]
        self.const_array_point_buy_even = [13, 13, 13, 12, 12, 12]
        self.const_array_point_buy_one_max = [15, 12, 12, 12, 11, 11]
        self.const_array_point_buy_two_max = [15, 15, 11, 10, 10, 10]
        self.const_array_point_buy_three_max = [15, 15, 15, 8, 8, 8]

        self.ability_label_array = ['Strength', 'Dexterity', 'Constitution',
                                    'Intelligence', 'Wisdom', 'Charisma']
        self.ability_dsc = {'Strength': "Natural athleticism, bodily power",
                            'Dexterity':
                            "Physical agility, reflexes, balance, poise",
                            'Constitution': "Health, stamina, vital force",
                            'Intelligence':
                            "Mental acuity, info recall, analytical skill",
                            'Wisdom': "Awareness, intuition, insight",
                            'Charisma': "Confidence, eloquence, leadership"}
        # self.class_eval = []
        if self.pref_array:
            ignore_pref_array = False
        else:
            ignore_pref_array = True


        jdict = {"used_array_type": array_type,
                 "used_pref_array": pref_array,
                 "ignore_pref_array": ignore_pref_array}

        self._populate()
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)


    def add_method_last_call_audit(self, audit_obj):
        self.method_last_call_audit[audit_obj['methodName']] = audit_obj

    def get_method_last_call_audit(self, method_name='ALL'):
        if method_name == 'ALL':
            return_val = self.method_last_call_audit
        else:
            return_val = self.method_last_call_audit[method_name]
        return return_val

    @ctx_decorator
    def _populate(self):
        """
        Populate a candidate array of Ability Scores
        """
        # standard = [15, 14, 13, 12, 10, 8]
        # point_buy_even = [13, 13, 13, 12, 12, 12]
        # point_buy_one_max = [15, 12, 12, 12, 11, 11]
        # point_buy_two_max = [15, 15, 11, 10, 10, 10]
        # point_buy_three_max = [15, 15, 15, 8, 8, 8]

        if self.array_type == "Predefined":
            self.candidate_array = self.raw_array
        elif self.array_type == "standard":
            self.candidate_array = self.const_array_standard
        elif self.array_type == "point_buy_even":
            self.candidate_array = self.const_array_point_buy_even
        elif self.array_type == "point_buy_one_max":
            self.candidate_array = self.const_array_point_buy_one_max
        elif self.array_type == "point_buy_two_max":
            self.candidate_array = self.const_array_point_buy_two_max
        elif self.array_type == "point_buy_three_max":
            self.candidate_array = self.const_array_point_buy_three_max
        else:
            d = Die(ctx=self.ctx, sides=6)
            for i in range(0, 6):
                if self.array_type == "strict":
                    pr = d.roll(rolls=3, droplowest=False)
                else:
                    pr = d.roll(rolls=4, droplowest=True)

                self.candidate_array.append(pr)

        # set the raw_array to whatever we started with for candidate values
        self.raw_array = self.candidate_array[:]

        # self.class_eval[-1]["raw_array"] = self.raw_array[:]

        jdict = {"raw_array": self.raw_array[:]}
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

        self.set_ability_array()

    @ctx_decorator
    def set_ability_array(self):
        self.set_ability_preferences()

        if self.racial_array:
            self.set_racial_adjustment()

    @ctx_decorator
    def set_preference_array(self, pref_array):
        self.pref_array = pref_array
        self.set_pref_str_array()
        self.ignore_pref_array = False
        self.set_ability_array()

    @ctx_decorator
    def set_pref_str_array(self):
        for p in range(len(self.pref_array)):
            if self.pref_array[p] == 0:
                self.pref_str_array[p] = 'Strength'
            elif self.pref_array[p] == 1:
                self.pref_str_array[p] = 'Dexterity'
            elif self.pref_array[p] == 2:
                self.pref_str_array[p] = 'Constitution'
            elif self.pref_array[p] == 3:
                self.pref_str_array[p] = 'Intelligence'
            elif self.pref_array[p] == 4:
                self.pref_str_array[p] = 'Wisdom'
            else:
                self.pref_str_array[p] = 'Charisma'

    def get_pref_str_array(self):
        return self.pref_str_array

    @ctx_decorator
    def set_ability_preferences(self):
        """
        Arrange the ability array by a defined order.
        """

        # if self.ignore_pref_array:
        if self.pref_array is None:
            self.ability_array = self.candidate_array[:]
        else:
            self.ability_array = [0, 0, 0, 0, 0, 0]

            # when applying ability preferences, it is assumed
            # that the array is sorted highest to lowest. Do that.
            self.candidate_array.sort(reverse=True)
            # loop through the prefArray putting the rolled scores
            # in the appropriate order.
            for pr in range(len(self.pref_array)):
                t = self.pref_array[pr]
                self.ability_array[t] = self.candidate_array[pr]

        self.pref_sorted_array = self.ability_array[:]

        self.numerical_sorted_array = self.candidate_array[:]
        jdict = { "numerical_sorted_array": self.candidate_array[:]}
        if self.pref_array:
            jdict["preference_array"] = self.pref_array[:]
            jdict["ability_array"] = self.ability_array[:]

        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    def get_raw_array(self):
        """
        Return the originally generated or received array
        """
        return self.raw_array

    def get_numerical_sorted_array(self):
        """
        Return the preference array
        """
        return self.numerical_sorted_array

    def get_pref_array(self):
        """
        Return the preference array
        """
        return self.pref_array

    def get_sorted_array(self):
        """
        Return the preference array
        """
        return self.pref_sorted_array

    def get_array(self):
        """
        Return an array of Ability Scores
        """
        return self.ability_array

    def get_imp_array(self):
        """
        Return the ability improvement array
        """
        return self.ability_imp_array

    def get_ability_labels(self):
        """
        Return the dictionary describing each of the Abilities
        """
        return self.ability_dsc

    # def get_class_eval(self):
    #     """
    #     Return an array of lists that can be used for debugging/testing
    #     """
    #     return self.class_eval

    @ctx_decorator
    def set_racial_array(self, bonus_array):
        self.racial_array = bonus_array
        jdict = {"racial_array": self.racial_array[:]}
        self.set_ability_array()
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def set_racial_adjustment(self):
        if self.ignore_racial_bonus:
            jdict = {"racial_adjustment": "Ignored"}
        else:
            for pr in range(len(self.ability_array)):
                self.ability_array[pr] = (
                    self.ability_array[pr] + self.racial_array[pr])
            jdict = {"racial_adjustment": self.ability_array[:]}
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)

    @ctx_decorator
    def ability_score_improvement(self):
        points = 2
        while points > 0:
            for pr in range(len(self.ability_array)):
                if self.ability_array[self.pref_array[pr]] < 19:
                    self.ability_array[self.pref_array[pr]] = (
                        self.ability_array[self.pref_array[pr]] + points)
                    self.ability_imp_array[self.pref_array[pr]] = (
                        self.ability_imp_array[self.pref_array[pr]] + points)
                    points = 0
                elif self.ability_array[self.pref_array[pr]] == 19:
                    self.ability_array[self.pref_array[pr]] = (
                        self.ability_array[self.pref_array[pr]] + 1)
                    self.ability_imp_array[self.pref_array[pr]] = (
                        self.ability_imp_array[self.pref_array[pr]] + 1)
                    points = (points - 1)
        jdict = {"ability_level_changes": self.ability_imp_array[:],
                 "ability_improvement": self.ability_array[:]}
        self.ctx.crumbs[-1].add_audit(json_dict=jdict)


if __name__ == '__main__':

    pref_array = [0, 5, 2, 4, 1, 3]
    ctx = Ctx(app_username='AbilityArray_main')
    a1 = AbilityArray(ctx=ctx, pref_array=pref_array)
    print(a1.get_raw_array())
    print(a1.get_numerical_sorted_array())
    print(a1.get_array())
    print(a1.get_method_last_call_audit())
    x = a1.get_method_last_call_audit(method_name='__init__')
    print(x)
    print(x['audit_json']['used_array_type'])
    print_method_last_call_audit(x=x)

    a = AbilityArray(ctx=ctx, array_type="Standard",
                     pref_array=string_to_array('5,0,2,1,4,3'),
                     racial_array=string_to_array('0,0,0,0,1,2'))
    print(a.get_raw_array())
    print(a.get_pref_array())
    print(a.get_array())
    # print(a.get_class_eval()[-1])
    # print("class eval:")
    # for key, value in a.get_class_eval()[-1].items():
    #     print(f"{str(key).ljust(25)}: {value}")
    # print("end class eval")
    a2 = AbilityArray(ctx=ctx, array_type="Common",
                      pref_array=string_to_array('1,2,5,0,4,3'))
    a2.set_racial_array(bonus_array=string_to_array('0,2,1,0,0,0'))
    print(a2.get_raw_array())
    print(a2.get_pref_array())
    print(a2.get_array())
    # print(a2.get_class_eval()[-1])
    # print("class eval:")
    # for key, value in a2.get_class_eval()[-1].items():
    #     print(f"{str(key).ljust(25)}: {value}")
    # print("end class eval")

    b = AbilityArray(ctx=ctx, array_type="Strict",
                     pref_array=string_to_array('5,0,2,1,4,3'),
                     racial_array=string_to_array('0,0,0,0,1,2'),
                     ignore_racial_bonus=True)
    print(b.get_raw_array())
    print(b.get_pref_array())
    print(b.get_array())
    # print(b.get_class_eval()[-1])
    # print("class eval:")
    # for key, value in b.get_class_eval()[-1].items():
    #     print(f"{str(key).ljust(25)}: {value}")
    # print("end class eval")

    b2 = AbilityArray(ctx=ctx, array_type="Predefined",
                      raw_array=string_to_array('6,6,6,6,6,6'),
                      pref_array=string_to_array('5,0,2,1,4,3'),
                      racial_array=string_to_array('0,0,0,0,1,2'),
                      ignore_racial_bonus=True)
    print(b2.get_raw_array())
    print(b2.get_pref_array())
    print(b2.get_array())
    # print(b2.get_class_eval()[-1])
    # print("class eval:")
    # for key, value in b2.get_class_eval()[-1].items():
    #     print(f"{str(key).ljust(25)}: {value}")
    # print("end class eval")

    c2 = AbilityArray(ctx=ctx)
    print(c2.get_raw_array())
    print(c2.get_pref_array())
    print(c2.get_array())
    # print(c2.get_class_eval()[-1])
    # print("class eval:")
    # for key, value in c2.get_class_eval()[-1].items():
    #     print(f"{str(key).ljust(25)}: {value}")
    # print("end class eval")
    print(c2.get_method_last_call_audit())



    comp_array = [13, 13, 13, 12, 12, 12]
    order_comp_array = [12, 12, 12, 13, 13, 13]
    pref_array = [5, 4, 3, 0, 1, 2]
    a = AbilityArray(ctx=ctx, array_type="point_buy_even", pref_array=pref_array)
    b = a.const_array_point_buy_even
    audit = a.get_method_last_call_audit()
    assert(audit['__init__']['audit_json']['used_array_type'] == 'point_buy_even')
    # for i in range(0, 6):
    #     assert(comp_array[i] == b[i])
    #     assert(comp_array[i] == b[audit['_populate']['audit_json']['raw_array'][i]]
    print(audit['__init__']['audit_json'])
    for i in range(0, 6):
        print(f"{comp_array[i]} == {b[i]}")
        print(f"{order_comp_array[i]} == {b[audit['__init__']['audit_json']['used_pref_array'][i]]}")