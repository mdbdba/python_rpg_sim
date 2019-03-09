from Die import Die
from CommonFunctions import arrayToString, stringToArray


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
                 raw_array=None,
                 pref_array=None,
                 racial_array=None,
                 ignore_racial_bonus=False,
                 debugInd=False):
        """
        Generate a list of values to serve as Ability Scores

        :param array_type: Choose the way the Ability Scores are created.
        :param pref_array: Array that defines how the rolls should be ordered.
        :param debugInd: log to classEval array? (default: False)
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
        self.classEval = []
        self.debugInd = debugInd
        if (self.pref_array):
            ignore_pref_array = False
        else:
            ignore_pref_array = True
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

        if self.array_type == "Predefined":
            self.candidate_array = self.raw_array
        elif self.array_type == "Standard":
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

        # set the raw_array to whatever we started with for candidate values
        self.raw_array = self.candidate_array[:]

        if self.debugInd:
            self.classEval[-1]["raw_array"] = self.raw_array[:]

        self.setAbilityPreferences()

        if self.racial_array:
            self.setRacialAdjustment()

    def setPreferenceArray(self, prefArray):
        self.pref_array = prefArray
        self.setPrefStrArray()
        self.ignore_pref_array = False
        self.setAbilityPreferences()
        if self.racial_array:
            self.setRacialAdjustment()

    def setPrefStrArray(self):
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

    def getPrefStrArray(self):
        return self.pref_str_array

    def setAbilityPreferences(self):
        """
        Arrange the ability array by a defined order.
        """

        # if self.ignore_pref_array:
        if (self.pref_array is None):
            self.ability_array = self.candidate_array[:]
        else:
            self.ability_array = [0, 0, 0, 0, 0, 0]

            # when applying ability preferences, it is assumed
            # that the array is sorted highest to lowest. Do that.
            self.candidate_array.sort(reverse=True)
            # loop through the prefArray putting the rolled scores
            # in the appropriate order.
            for r in range(len(self.pref_array)):
                t = self.pref_array[r]
                self.ability_array[t] = self.candidate_array[r]

        self.pref_sorted_array = self.ability_array[:]

        if self.debugInd and "ability_base_array" in self.classEval[-1]:
            self.classEval.append({"call": "setAbilityPreferences"})

        self.numerical_sorted_array = self.candidate_array[:]
        self.classEval[-1]["numerical_sorted_array"] = self.candidate_array[:]
        if (self.pref_array):
            self.classEval[-1]["preference_array"] = self.pref_array[:]
        self.classEval[-1]["ability_array"] = self.ability_array[:]

    def getRawArray(self):
        """
        Return the originally generated or received array
        """
        return self.raw_array

    def getNumericalSortedArray(self):
        """
        Return the preference array
        """
        return self.numerical_sorted_array

    def getPrefArray(self):
        """
        Return the preference array
        """
        return self.pref_array

    def getSortedArray(self):
        """
        Return the preference array
        """
        return self.pref_sorted_array

    def getArray(self):
        """
        Return an array of Ability Scores
        """
        return self.ability_array

    def getImpArray(self):
        """
        Return the ability improvement array
        """
        return self.ability_imp_array

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

    def setRacialArray(self, bonusArray):
        self.racial_array = bonusArray
        self.classEval[-1]["racial_array"] = self.racial_array[:]
        self.setRacialAdjustment()

    def setRacialAdjustment(self):
        if (self.ignore_racial_bonus):
            self.classEval[-1]["racial_adjustment"] = "Ignored"
        else:
            for r in range(len(self.ability_array)):
                self.ability_array[r] = (
                    self.ability_array[r] + self.racial_array[r])
            self.classEval[-1]["racial_adjustment"] = self.ability_array[:]

    def abilityScoreImprovement(self):
        points = 2
        while (points > 0):
            for r in range(len(self.ability_array)):
                if (self.ability_array[self.pref_array[r]] < 19):
                    self.ability_array[self.pref_array[r]] = (
                        self.ability_array[self.pref_array[r]] + points)
                    self.ability_imp_array[self.pref_array[r]] = (
                        self.ability_imp_array[self.pref_array[r]] + points)
                    points = 0
                elif (self.ability_array[self.pref_array[r]] == 19):
                    self.ability_array[self.pref_array[r]] = (
                        self.ability_array[self.pref_array[r]] + 1)
                    self.ability_imp_array[self.pref_array[r]] = (
                        self.ability_imp_array[self.pref_array[r]] + 1)
                    points = (points - 1)
        self.classEval[-1]["ability_level_changes"] = self.ability_imp_array[:]
        self.classEval[-1]["ability_improvement"] = self.ability_array[:]


if __name__ == '__main__':
    a1 = AbilityArray()
    print(a1.getRawArray())
    print(a1.getPrefArray())
    print(a1.getArray())
    print(a1.getClassEval())
    x = a1.getClassEval()
    print("class eval:")
    for r in range(len(x)):
        for key, value in x[r].items():
            print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")

    a = AbilityArray(array_type="Standard",
                     pref_array=stringToArray('5,0,2,1,4,3'),
                     racial_array=stringToArray('0,0,0,0,1,2'),
                     debugInd=True)
    print(a.getRawArray())
    print(a.getPrefArray())
    print(a.getArray())
    print(a.getClassEval()[-1])
    print("class eval:")
    for key, value in a.getClassEval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")
    a2 = AbilityArray(array_type="Common",
                      pref_array=stringToArray('1,2,5,0,4,3'),
                      debugInd=True)
    a2.setRacialArray(stringToArray('0,2,1,0,0,0'))
    print(a2.getRawArray())
    print(a2.getPrefArray())
    print(a2.getArray())
    print(a2.getClassEval()[-1])
    print("class eval:")
    for key, value in a2.getClassEval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")

    b = AbilityArray(array_type="Strict",
                     pref_array=stringToArray('5,0,2,1,4,3'),
                     racial_array=stringToArray('0,0,0,0,1,2'),
                     ignore_racial_bonus=True,
                     debugInd=True)
    print(b.getRawArray())
    print(b.getPrefArray())
    print(b.getArray())
    print(b.getClassEval()[-1])
    print("class eval:")
    for key, value in b.getClassEval()[-1].items():
        print(f"{str(key).ljust(25)}: {value}")
    print("end class eval")
