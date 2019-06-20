import math
import os, fnmatch

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


def dictToString(srcDict, linebreaks=False, leftJustify=0):
    retStr = ""
    if (linebreaks):
        el = '\n'
    else:
        el = ", "
    for key, value in srcDict.items():
        retStr = (f"{retStr}{str(key).ljust(leftJustify)}: {value}{el}")

    if (not linebreaks):
        retStr = retStr[:-2]

    return retStr

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    dist: float = (math.sqrt((x2 - x1)**2 + (y2 - y1)**2)) * 5
    return dist

def find_file(file_name: str) -> str:
    curpath = os.path.abspath(os.path.dirname(__file__))
    for root, dirs, files in os.walk(curpath):
        for name in files:
            if fnmatch.fnmatch(name, file_name):
                return os.path.join(root, name)

    curpath = sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    print(curpath)
    for file in os.listdir(curpath):
        if fnmatch.fnmatch(file, file_name):
            return os.path.join(curpath, file)

