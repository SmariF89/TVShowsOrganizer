#!/usr/bin/env python
from difflib import SequenceMatcher
from pathlib import Path
from shutil import copy
import argparse
import re
import os

# Checks if a given file is a TV show using its file extension.
def isTVShow(filePath):
    filePathStr = str(filePath)
    if(".torrent" in filePathStr): return False
    if(".nfo" in filePathStr): return False
    if(".jpg" in filePathStr): return False
    if(".mta" in filePathStr): return False
    if(".db" in filePathStr): return False
    if(".part" in filePathStr): return False
    if("sample" in filePathStr): return False
    if(".srt" in filePathStr): return False
    if(".png" in filePathStr): return False
    if(".mta" in filePathStr): return False
    return True

# Checks if input string contains digits.
def containsDigit(stringInput):
    for s in stringInput:
        if(s.isdigit()): return True
    return False

# Checks two strings for likeness. Returns percentage.
def similar(stringA, stringB):
    return SequenceMatcher(None, stringA, stringB).ratio()

# Scans file history and checks if current filename is similar to
# any other already found file.
def checkSimilarity(showNameSet, showName):
    for sName in showNameSet:
        if(similar(sName, showName) > 0.92):
            return sName
    return

# str is some minimum info about a season number.
# Returns the info in the form of Season #.
def seasonFormat(str):
    res = re.findall(r"[0-9]+", str)
    if not res:
        return
    seasonNo = res[0]
    if len(seasonNo) == 1:
        return "Season " + "0" + seasonNo
    return "Season " + seasonNo

# Capitalizes each letter of a show name, removes extra
# whitespaces and other symbols.
def titleFormat(inp):
    inp = inp.strip(" ")
    if inp == "":
        return ""

    units = inp.split()
    product = ""
    for u in units:
        if u[0].islower():
            product += u[0].capitalize() + u[1:] + " "
        else:
            product += u + " "

    product = product.split("(")[0]
    return product.strip("- ").strip("[ ")

# Checks if a parent folder name is an abbreviation of show name.
def checkInitialsInParentName(child, parent):
    tmpStr = ""
    for word in parent.split():
         tmpStr += word[0].capitalize()

    if(tmpStr == child): return parent
    return child

# Cleverly recognizes TV shows in folder structure (sourceFolder),
# copies them into another neatly organised folder (targetFolder).
def clean(sourceFolder, targetFolder):

    ### REGEX DECLARATIONS ###

    # Example: S05E02 or S2 E 09 or s15e03
    # Group01: Name of show
    # Group02: Season number
    # Group03: File extension
    formatAlpha= re.compile(r"(.*)([Ss][0-9]?[ ]?[0-9][ ]?)[Ee][ ]?[0-9]?[0-9]?.*(\.mp4|\.mkv|\.avi|\.mpg)")

    # Example: 24.905.hdtv-lol.mp4 or Seinfeld 0609 The Secretary.avi
    # Group01: Name of show
    # Group02: Season number
    # Group03: File extension
    formatBeta = re.compile(r"(.*)([0-9]?[0-9])[0-9][0-9][^p]hdtv.*(\.mp4|\.mkv|\.avi|\.mpg)")

    # Example: Misfits - 202.avi or Spooks - 08 -.avi
    # Group01: Name of show
    # Group02: Season number
    # Group03: File extension
    formatGamma = re.compile(r"(.*)[ ]*-[ ]*([0-9]).*(\.mp4|\.mkv|\.avi|\.mpg)")

    # Example: Seinfeld 0407 The Bubble Boy.avi
    # Group01: Name of show
    # Group02: Season number
    # Group03: File extension
    formatDelta = re.compile(r"([A-Za-z]+)[ ]?[0-9]([0-9])[0-9]*.*(\.mp4|\.mkv|\.avi|\.mpg)")

    # Example: 204a - Power Animal.mp4 or 104 - My Old Lady.avi
    # Group01: Season number
    # Group02: Name of show
    # Group03: File extension
    formatEpsilon = re.compile(r"([0-9])[0-9]+[a-zA-Z]?[ ]*-[ ]*(.*).*(\.mp4|\.mkv|\.avi|\.mpg)")

    # Example: Top Gear - [17x03] - 2011.07.10 [RiVER].avi or downton_abbey.3x06.hdtv_x264-fov.mp4
    # Group01: Name of show
    # Group02: Season number
    # Group03: File extension
    formatZeta = re.compile(r"(.+?)([0-9]{1,2})[xX][0-9]{1,2}.*(\.mp4|\.mkv|\.avi|\.mpg)")

    # Example: Breaking Bad - Season 2 - Episode 06.avi
    # Group01: Name of show
    # Group02: Season number
    # Group03: File extension
    formatTheta = re.compile(r"(.*)[ ]*-[ ]*Season[ ]*([0-9]{1,2})[ ]*-[ ]*.*(\.mp4|\.mkv|\.avi|\.mpg)")

    ### MAIN LOOP ###
    # Walks through the folder structure and inspects every file by applying regex to it in order to
    # recognize if it is a TV show or not. If none of the regex catches it a final check is made by
    # inspecting its parent folder names. If all of the eight checks fail, file is not a TV show and
    # is ignored, else it is copied to its designated folder.

    p = Path(sourceFolder)
    showNameSet = set()
    for root, dirs, files in os.walk(sourceFolder):
        for file in files:

            # This boolean will be True if a show is found.
            # If True, copy to designated folder.
            foundShow = False

            # Attempting matches.
            matchFoundAlpha = formatAlpha.match(file)
            matchFoundBeta = formatBeta.match(file)
            matchFoundGamma = formatGamma.match(file)
            matchFoundDelta = formatDelta.match(file)
            matchFoundEpsilon = formatEpsilon.match(file)
            matchFoundZeta = formatZeta.match(file)
            matchFoundTheta = formatTheta.match(file)

            if matchFoundAlpha and "sample" not in file.lower() and not file.endswith(".part"):
                if matchFoundAlpha.group(1):
                    showName = titleFormat(matchFoundAlpha.group(1).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundAlpha.group(2))
                elif not matchFoundAlpha.group(1) and "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundAlpha.group(2))
                else:
                    showName = titleFormat(matchFoundAlpha.group(1))
                    seasonName = seasonFormat(matchFoundAlpha.group(2))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif matchFoundBeta and "sample" not in file.lower() and not file.endswith(".part"):
                if matchFoundBeta.group(1):
                    showName = titleFormat(matchFoundBeta.group(1).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundBeta.group(2))
                elif not matchFoundBeta.group(1) and "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundBeta.group(2))
                else:
                    showName = titleFormat(matchFoundBeta.group(1))
                    seasonName = seasonFormat(matchFoundBeta.group(2))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif matchFoundDelta and "sample" not in file.lower() and not file.endswith(".part"):
                if matchFoundDelta.group(1):
                    showName = titleFormat(matchFoundDelta.group(1).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundDelta.group(2))
                elif not matchFoundDelta.group(1) and "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundDelta.group(2))
                else:
                    showName = titleFormat(matchFoundDelta.group(1))
                    seasonName = seasonFormat(matchFoundDelta.group(2))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif matchFoundGamma and "sample" not in file.lower() and not file.endswith(".part"):
                if matchFoundGamma.group(1):
                    showName = titleFormat(matchFoundGamma.group(1).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundGamma.group(2))
                elif not matchFoundGamma.group(1) and "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundGamma.group(2))
                else:
                    showName = titleFormat(matchFoundGamma.group(1))
                    seasonName = seasonFormat(matchFoundGamma.group(2))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif matchFoundEpsilon and "sample" not in file.lower() and not file.endswith(".part"):
                if "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundEpsilon.group(1))
                elif matchFoundEpsilon.group(1):
                    showName = titleFormat(matchFoundEpsilon.group(2).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundEpsilon.group(1))
                else:
                    showName = titleFormat(matchFoundEpsilon.group(2))
                    seasonName = seasonFormat(matchFoundEpsilon.group(1))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif matchFoundZeta and "sample" not in file.lower() and not file.endswith(".part"):
                if matchFoundZeta.group(1):
                    showName = titleFormat(matchFoundZeta.group(1).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundZeta.group(2))
                elif not matchFoundZeta.group(1) and "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundZeta.group(2))
                else:
                    showName = titleFormat(matchFoundZeta.group(1))
                    seasonName = seasonFormat(matchFoundZeta.group(2))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif matchFoundTheta and "sample" not in file.lower() and not file.endswith(".part"):
                if matchFoundTheta.group(1):
                    showName = titleFormat(matchFoundTheta.group(1).replace(".", " ").replace("'", "").replace("-", " "))
                    showName = checkInitialsInParentName(showName, Path(root + os.sep + file).parent.name)
                    seasonName = seasonFormat(matchFoundTheta.group(2))
                elif not matchFoundTheta.group(1) and "season" in Path(root + os.sep + file).parent.name.lower():
                    showName = Path(root + os.sep + file).parent.parent.name
                    seasonName = seasonFormat(matchFoundTheta.group(2))
                else:
                    showName = titleFormat(matchFoundTheta.group(1))
                    seasonName = seasonFormat(matchFoundTheta.group(2))

                rShowName = checkSimilarity(showNameSet, showName)
                if(not rShowName): showNameSet.add(showName)
                else: showName = rShowName

                foundShow = True

            elif "season" in Path(root + os.sep + file).parent.name.lower() and file[0].isdigit() and isTVShow(Path(root + os.sep + file)):
                if(containsDigit(Path(root + os.sep + file).parent.parent.name)):
                    showName = Path(root + os.sep + file).parent.parent.name.replace("'", "")
                    seasonName = seasonFormat(Path(root + os.sep + file).parent.name)

                    foundShow = True

            # A match was found. Copy to designated folder.
            if foundShow:
                sourcePath = Path(root + os.sep + file)
                newPath = targetFolder + os.sep + showName + os.sep + seasonName
                if not os.path.exists(newPath):
                    os.makedirs(newPath)
                copy(sourcePath, newPath)

# This ables the user to apply the script via commandline parameters.
def main(args):
    if not os.path.exists(args.pathToDest):
        os.mkdir(args.pathToDest)

    clean(args.pathToSource, args.pathToDest)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean downloads folder.')
    parser.add_argument('pathToSource', metavar='FILE')
    parser.add_argument('pathToDest', metavar='FILE')
    args = parser.parse_args()
    main(args)
