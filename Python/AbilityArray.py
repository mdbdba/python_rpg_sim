from Die import Die
# from CommonFunctions import array_to_string, string_to_array
from CommonFunctions import string_to_array


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
    def __init__(self, array_type="Common",
                 raw_array=None,
                 pref_array=None,
                 racial_array=None,
                 ignore_racial_bonus=False,
                 debug_ind=False):
        """
        Generate a list of values to serve as Ability Scores

        :param array_type: Choose the way the Ability Scores are created.
        :param pref_array: Array that defines how the rolls should be ordered.
        :param racial_array:
        :param ignore_racial_bonus: Ignore ability bonuses for races.
        :param debug_ind: log to class_eval array? (default: False)
        """
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
        self.class_eval = []
        self.debug_ind = debug_ind
        if self.pref_array:
            ignore_pref_array = False
        else:
            ignore_pref_array = True
        self.class_eval.append({"array_type": array_type,
                                "pref_array": pref_array,
                                "ignore_pref_array": ignore_pref_array,
                                "debug_ind": debug_ind})
        self._populate()

    def _populate(self):
        """
        Populate a candidate array of Ability Scores
        """
        standard = [15, 14, 13, 12, 10, 8]
        point_buy_even = [13, 13, 13, 12, 12, 12]
        point_buy_one_max = [15, 12, 12, 12, 11, 11]
        point_buy_two_max = [15, 15, 11, 10, 10, 10]
        point_buy_three_max = [15, 15, 15, 8, 8, 8]

        if self.array_type == "Predefined":
            self.candidate_array = self.raw_array
        elif self.array_type == "standard":
            self.candidate_array = standard
        elif self.array_type == "point_buy_even":
            self.candidate_array = point_buy_even
        elif self.array_type == "point_buy_one_max":
            self.candidate_array = point_buy_one_max
        elif self.array_type == "point_buy_two_max":
            self.candidate_array = point_buy_two_max
        elif self.array_type == "point_buy_three_max":
            self.candidate_array = point_buy_three_max
        else:
            d = Die(6)
            for i in range(0, 6):
                if self.array_type == "strict":
                    pr = d.roll(3, False)
                else:
                    pr = d.roll(4, True)

                self.candidate_array.append(pr)

        # set the raw_array to whatever we started with for candidate values
        self.raw_array = self.candidate_array[:]

        if self.debug_ind:
            self.class_eval[-1]["raw_array"] = self.raw_array[:]

        self.set_ability_array()

    def set_ability_array(self):
        self.set_ability_preferences()

        if self.racial_array:
            self.set_racial_adjustment()

    def set_preference_array(self, pref_array):
        self.pref_array = pref_array
        self.set_pref_str_array()
        self.ignore_pref_array = False
        self.set_ability_array()

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

        if self.debug_ind and "ability_base_array" in self.class_eval[-1]:
            self.class_eval.append({"call": "set_ability_preferences"})

        self.numerical_sorted_array = self.candidate_array[:]
        self.class_eval[-1]["numerical_sorted_array"] = self.candidate_array[:]
        if self.pref_array:
            self.class_eval[-1]["preference_array"] = self.pref_array[:]
        self.class_eval[-1]["ability_array"] = self.ability_array[:]

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

    def get_class_eval(self):
        """
        Return an array of lists that can be used for debugging/testing
        """
        return self.class_eval

    def set_racial_array(self, bonus_array):
        self.racial_array = bonus_array
        self.class_eval[-1]["racial_array"] = self.racial_array[:]
        self.set_ability_array()

    def set_racial_adjustment(self):
        if self.ignore_racial_bonus:
            self.class_eval[-1]["racial_adjustment"] = "Ignored"
        else:
            for pr in range(len(self.ability_array)):
                self.ability_array[pr] = (
                    self.ability_array[pr] + self.racial_array[pr])
            self.class_eval[-1]["racial_adjustment"] = self.ability_array[:]

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
        self.class_eval[-1]["ability_level_changes"] = self.ability_imp_array[:]
        self.class_eval[-1]["ability_improvement"] = self.ability_array[:]


if __name__ == '__main__':

    pref_array=[0,5,2,4,1,3]
    a1 = AbilityArray(pref_array=pref_array)
    print(a1.get_raw_array())
    print(a1.get_numerical_sorted_array())
    print(a1.get_array())
    print(a1.get_class_eval())
    x = a1.get_class_eval()
    print("class eval:")
    for r in range(len(x)):
        for key, value in x[r].items():
            print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")

    a = AbilityArray(array_type="Standard",
                     pref_array=string_to_array('5,0,2,1,4,3'),
                     racial_array=string_to_array('0,0,0,0,1,2'),
                     debug_ind=True)
    print(a.get_raw_array())
    print(a.get_pref_array())
    print(a.get_array())
    print(a.get_class_eval()[-1])
    print("class eval:")
    for key, value in a.get_class_eval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")
    a2 = AbilityArray(array_type="Common",
                      pref_array=string_to_array('1,2,5,0,4,3'),
                      debug_ind=True)
    a2.set_racial_array(string_to_array('0,2,1,0,0,0'))
    print(a2.get_raw_array())
    print(a2.get_pref_array())
    print(a2.get_array())
    print(a2.get_class_eval()[-1])
    print("class eval:")
    for key, value in a2.get_class_eval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")

    b = AbilityArray(array_type="Strict",
                     pref_array=string_to_array('5,0,2,1,4,3'),
                     racial_array=string_to_array('0,0,0,0,1,2'),
                     ignore_racial_bonus=True,
                     debug_ind=True)
    print(b.get_raw_array())
    print(b.get_pref_array())
    print(b.get_array())
    print(b.get_class_eval()[-1])
    print("class eval:")
    for key, value in b.get_class_eval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")

    b2 = AbilityArray(array_type="Predefined",
                      raw_array=string_to_array('6,6,6,6,6,6'),
                      pref_array=string_to_array('5,0,2,1,4,3'),
                      racial_array=string_to_array('0,0,0,0,1,2'),
                      ignore_racial_bonus=True,
                      debug_ind=True)
    print(b2.get_raw_array())
    print(b2.get_pref_array())
    print(b2.get_array())
    print(b2.get_class_eval()[-1])
    print("class eval:")
    for key, value in b2.get_class_eval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")