from Die import Die


"""
Class for generating Ability Arrays.
Parameters:
    array_type describes how we want the array created
    choices are:
        Common  (Default) -- roll 4d6 and drop the lowest.
        Strict            -- roll 3d6. Keep the numbers as is.
        Standard          -- [15, 14, 13, 12, 10, 8]
        PointBuy_Even        [13, 13, 13, 12, 12 ,12]
        PointBuy_OneMax   -- [15, 12, 12, 12, 11, 11]
        PointBuy_TwoMax   -- [15, 15, 11, 10, 10, 10]
        PointBuy_ThreeMax -- [15, 15, 15, 8, 8, 8]
"""


class AbilityArray(object):
    def __init__(self, array_type="Common",
                 pref_array=[3, 2, 1, 5, 4, 0],
                 ignore_pref_array=False,
                 debugInd=False):
        """
        Generate a list of values to serve as Ability Scores

        :param array_type: Choose the way the Ability Scores are created.
        :param pref_array: Array that defines how the rolls should be ordered.
        :param ignore_pref_array: if True, use values as they were rolled.
        :param debugInd: log to classEval array? (default: False)
        """
        self.array_type = array_type
        self.pref_array = pref_array
        self.ability_base_array = []
        self.ability_dsc = {'Strength': "Natural athleticism, bodily power",
                            'Dexterity':
                            "Physical agility, reflexes, balance, poise",
                            'Constitution': "Health, stamina, vital force",
                            'Intelligence':
                            "Mental acuity, info recall, analytical skill",
                            'Wisdom': "Awareness, intuition, insight",
                            'Charisma': "Confidence, eloquence, leadership"}
        self.ignore_pref_array = ignore_pref_array
        self.candidate_array = []
        self.ability_base_array = []
        self.classEval = []
        self.debugInd = debugInd
        self.classEval.append({"array_type": array_type,
                               "pref_array": pref_array,
                               "ignore_pref_array": ignore_pref_array,
                               "debugInd": debugInd})

        self._populate()

    def _populate(self):
        """
        Populate a candidate array of Ability Scores
        """
        Standard = [15, 14, 13, 12, 10, 8]
        PointBuy_Even = [13, 13, 13, 12, 12, 12]
        PointBuy_OneMax = [15, 12, 12, 12, 11, 11]
        PointBuy_TwoMax = [15, 15, 11, 10, 10, 10]
        PointBuy_ThreeMax = [15, 15, 15, 8, 8, 8]

        if self.array_type == "Standard":
            self.candidate_array = Standard
        elif self.array_type == "PointBuy_Even":
            self.candidate_array = PointBuy_Even
        elif self.array_type == "PointBuy_OneMax":
            self.candidate_array = PointBuy_OneMax
        elif self.array_type == "PointBuy_TwoMax":
            self.candidate_array = PointBuy_TwoMax
        elif self.array_type == "PointBuy_ThreeMax":
            self.candidate_array = PointBuy_ThreeMax
        else:
            d = Die(6)
            for i in range(0, 6):
                if self.array_type == "Strict":
                    r = d.roll(3, False)
                else:
                    r = d.roll(4, True)

                self.candidate_array.append(r)

        if self.debugInd:
            self.classEval[-1]["candidate_array"] = self.candidate_array[:]

        self.setAbilityPreferences(self.pref_array)

    def setAbilityPreferences(self, prefArray):
        """
        Arrange the ability array by a defined order.

        :param prefArray: array describing the order
        """

        if self.ignore_pref_array:
            self.ability_base_array = self.candidate_array[:]
        else:
            self.ability_base_array = [0, 0, 0, 0, 0, 0]

            # when applying ability preferences, it is assumed
            # that the array is sorted highest to lowest. Do that.
            self.candidate_array.sort(reverse=True)
            # loop through the prefArray putting the rolled scores
            # in the appropriate order.
            for r in range(len(prefArray)):
                t = prefArray[r]
                self.ability_base_array[t] = self.candidate_array[r]

        if self.debugInd and "ability_base_array" in self.classEval[-1]:
            self.classEval.append({"call": "setAbilityPreferences"})

        self.classEval[-1]["sorted_candidate_array"] = self.candidate_array[:]
        self.classEval[-1]["preference_array"] = prefArray[:]
        self.classEval[-1]["ability_base_array"] = self.ability_base_array[:]

    def getArray(self):
        """
        Return an array of Ability Scores
        """
        return self.ability_base_array

    def getAbilityLabels(self):
        """
        Return the dictionary describing each of the Abilities
        """
        return self.ability_dsc

    def getClassEval(self):
        """
        Return an array of lists that can be used for debugging/testing
        """
        return self.classEval


if __name__ == '__main__':
    a1 = AbilityArray()
    print(a1.getArray())
    print(a1.getClassEval())
    a = AbilityArray(array_type="Standard",
                     ignore_pref_array=True,
                     debugInd=True)
    b = a.getArray()
    c = a.getClassEval()[-1]
    print(b)
    print(c)
