
def arrayToString(srcArray):
    outstr = ""
    for a in range(len(srcArray)):
        outstr = (f"{outstr}{srcArray[a]},")
    outstr = outstr[:-1]

    return outstr


def stringToArray(srcStr, delimiter=","):
    strArray = srcStr.split(delimiter)
    outArray = []
    for a in range(len(strArray)):
        outArray.append(int(strArray[a].strip()))

    return outArray


def compareArrays(array1, array2):
    retval = True
    if (len(array1) != len(array2)):
        retval = False
    for a in range(len(array1)):
        if (array1[a] != array2[a]):
            retval = False

    return retval


def inchesToFeet(inches):
    feet = inches // 12
    remainder = inches % 12
    return (f"{feet}'{remainder}\"")
