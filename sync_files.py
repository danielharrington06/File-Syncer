#Daniel Harrington
#Sync Files

#This program aims to sync the files of two directories

#It should log any changes made.

#It will take the most recent copy of files and copy this
#It will copy files that do not exist in the other directory

import os #to walk through the directories
import configparser #to configure the setup
import time
import datetime
import shutil # used to copy
import random

global actions
actions = ["X", "S", "C", "R", "N", "E", "A", "D", "F", "CM", "NM", "P", " "]

global output
output = []

global suggestedChanges
suggestedChanges = 0

global changesMade
changesMade = 0

global totalChecks
global totalDifferences
global percentageSynced

global elapsedTime


startTime = time.time()

# folderOnePath = f1 + addition + "\\" + fileORfolder
# parentOnePath = f1 + addition

def findNotCommon(root, dirPath):
    output = ""
    output = dirPath[len(root):]
    return output

def getDate(root, addition, fileName, dateParam):
    filePath = root + addition + "\\" + fileName
    if dateParam == "lastMod": #gets unix stamp of last modified date/time
        date = os.path.getmtime(filePath)
    elif dateParam == "firstCreate": #gets unix stamp of creation date/time
        date = os.path.getctime(filePath)
    elif dateParam == "lastAccess":
        date = os.path.getatime(filePath)
    else:
        date = os.path.getmtime(filePath)

    return date

def getSize(root, addition, fileName, unit):
    possibleUnits = ["B", "KB", "MB", "GB", "TB", "PB"]
    filePath = root + addition + "\\" + fileName
    
    size = os.path.getsize(filePath)

    if unit == "B":
        unit = "B"
    elif unit == "smallest":
        unit = "B"
        while size >= 1024:
            size /= 1024
            unit = possibleUnits[possibleUnits.index(unit)+1]

        size = f"{size:.2f}"

    return size, unit

def getConfig():
    global folderOne
    global folderOneName
    global folderTwo
    global folderTwoName
    global mode
    global logfileLocation
    global compareDateParameter
    global logErrorNoFolderOne
    global deletedfileLocation
    global askWhenDateDif
    global calcPercentage

    config = configparser.ConfigParser()
    config.read("sync_config.ini")

    folderOne = config["DEFAULT"]["folderOne"]
    folderOneName = config["DEFAULT"]["folderOneName"]
    folderTwo = config["DEFAULT"]["folderTwo"]
    folderTwoName = config["DEFAULT"]["folderTwoName"]
    mode = config["DEFAULT"]["mode"]
    logfileLocation = config["DEFAULT"]["logfileLocation"]
    compareDateParameter = config["DEFAULT"]["compareDateParameter"]
    logErrorNoFolderOne = bool(int(config["DEFAULT"]["logErrorNoFolderOne"]))
    deletedfileLocation = config["DEFAULT"]["deletedfileLocation"]
    askWhenDateDif = bool(int(config["DEFAULT"]["askWhenDateDif"]))
    calcPercentage = bool(int(config["DEFAULT"]["calcPercentage"]))

def evalActionFile(f1, f1N, f2, f2N, addition, fileName):
    global totalChecks
    global totalDifferences
    #parent1 and parent2 are the larger directories that lead to the file

    # actions:
    # C - Copy 1 to 2 (when 2 does not exist)
    # R - Replace - delete 2 (when 1 is better state than 2) and copy 1 to 2
    # N - No action required
    # E - Error - first file/folder not found

    suggestedAction = "N"
    action = "N"

    fileOnePath = f1 + addition + "\\" + fileName
    fileTwoPath = f2 + addition + "\\" + fileName

    if os.path.exists(fileOnePath):
        if os.path.exists(fileTwoPath):
            #compare dates and file sizes
            fileSizeOne, unitOne = getSize(f1, addition, fileName, "B") #measured in Bytes
            fileSizeTwo, unitTwo = getSize(f2, addition, fileName, "B") #measured in Bytes

            fileDateOne = getDate(f1, addition, fileName, compareDateParameter) #in unix time
            fileDateTwo = getDate(f2, addition, fileName, compareDateParameter) #in unix time

            if fileSizeOne == fileSizeTwo: #if file size the same, probably no need to do anything
                suggestedAction = "N"
                
                if mode == "action": #if file size same, still should give option to not do this
                    if fileDateOne == fileDateTwo: 
                        action = "N"
                        x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)

                    elif askWhenDateDif == True:
                        #get confirmation/decision
                        action = " "
                        x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)
                        executeAction(f1, f1N, f2, f2N, addition, fileName, suggestedAction, "")
                        suggestedAction = "N"
                    else: #when date is different between two files but size is same and ask when date is differnt is false
                        action = "N"
                        x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)
                
                else:
                    x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)
            else: #if file sizes different, compare based off comparison date parameter
                
                #higher unix number means higher 
                if fileDateOne > fileDateTwo: #if file one is newer than file two based off date param
                    suggestedAction = "R"
                    x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)

                    if mode == "action":
                        #get confirmation/decision
                        executeAction(f1, f1N, f2, f2N, addition, fileName, suggestedAction, "")
                        suggestedAction = "N"
                        #actions are N or R
                        pass


            pass
        else:
            #copy from 1 to 2
            suggestedAction = "C"
            x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)

            if mode == "action":
                #get confirmation/decision
                executeAction(f1, f1N, f2, f2N, addition, fileName, suggestedAction, "")
                suggestedAction = "N"
                #actions are C or N
                pass
            pass
    else:
        suggestedAction = "E"
        action = "E"
        x = log(f1, f1N, f2, f2N, addition, fileName, suggestedAction, action)

    if calcPercentage == True:
        if suggestedAction != "N" and os.path.exists(fileOnePath):
            totalDifferences += 1
        if os.path.exists(fileOnePath):
            totalChecks += 1

def evalActionFolder(f1, f1N, f2, f2N, addition, folderName):
    global totalChecks
    global totalDifferences
     #parent1 and parent2 are the larger directories that lead to the file

    # actions:
    
    # N - No action required
    # E - Error - first file/folder not found
    # A - Add a new folder

    suggestedAction = "N"
    action = "N"

    folderOnePath = f1 + addition + "\\" + folderName
    folderTwoPath = f2 + addition + "\\" + folderName

    if os.path.exists(folderOnePath):
        if os.path.exists(folderTwoPath):
            #does nothing as both exist
            suggestedAction = "N"
            x = log(f1, f1N, f2, f2N, addition, folderName, suggestedAction, action)
            
        else:
            #second is not present, so most likely should make new folder
            suggestedAction = "A"
            x = log(f1, f1N, f2, f2N, addition, folderName, suggestedAction, action)

            if mode == "action":
                #get confirmation/decision
                executeAction(f1, f1N, f2, f2N, addition, folderName, suggestedAction, "")
                suggestedAction = "N"
                #actions are A or N
                pass
    else:
        suggestedAction = "E"
        action = "E"
        x = log(f1, f1N, f2, f2N, addition, folderName, suggestedAction, action)

    if calcPercentage == True:
        if suggestedAction != "N" and os.path.exists(folderOnePath):
            totalDifferences += 1
        if os.path.exists(folderOnePath):
            totalChecks += 1


def executeAction(f1, f1N, f2, f2N, addition, fileORfolder, suggestedAction, action):
    global changesMade
    #parent1 and parent2 are the larger directories that lead to the file/folder

    #executable actions are:
    # C - Copy 1 to 2 (when 2 does not exist)
    # R - Replace - delete 2 (when 1 is better state than 2) and copy 1 to 2
    # N - No action required
    # A - Add a new folder

    if mode == "action":

        action = log(f1, f1N, f2, f2N, addition, fileORfolder, suggestedAction, action)

        #do all the actions
        if action == "N" or action == "E":

            log("", "", "", "", "", "", "NM", action)

        elif action == "D": #deletes path1 file/folder

            fileORfolderPathOne = f1 + addition + "\\" + fileORfolder

            if os.path.isdir(fileORfolderPathOne) == True:

                try:
                    shutil.copytree(fileORfolderPathOne, deletedfileLocation + "\\" + fileORfolder + str(random.randint(1,10000))) #copies to bin location
                    shutil.rmtree(fileORfolderPathOne) #can delete an empty folder
                    
                    changesMade += 1
                    log("", "", "", "", "", "", "CM", action)
                    

                except:
                    log("", "", "", "", "", "", "NM", action)

            elif os.path.isfile(fileORfolderPathOne) == True:

                try:
                    shutil.copy2(fileORfolderPathOne, deletedfileLocation) #copies to bin location
                    print("Shutil copy2")
                    os.remove(fileORfolderPathOne)
                    print("Os remove")

                    changesMade += 1
                    log("", "", "", "", "", "", "CM", action)
                    

                except:
                    log("", "", "", "", "", "", "NM", action)    

        elif action == "C": #copies file1 to path2
            
            try:
                filePathOne = f1 + addition + "\\" + fileORfolder
                folderPathTwo = f2 + addition

                shutil.copy2(filePathOne, folderPathTwo)

                log("", "", "", "", "", "", "CM", action)
                changesMade += 1

            except:
                log("", "", "", "", "", "", "NM", action)    
            

        elif action == "R": #delete file2 and copy file1 to path2
            filePathOne = f1 + addition + "\\" + fileORfolder
            filePathTwo = f2 + addition + "\\" + fileORfolder
            folderPathTwo = f2 + addition

            if os.path.isfile(filePathTwo) == True:

                try:
                    shutil.copy2(filePathTwo, deletedfileLocation) #copies to bin location
                    os.remove(filePathTwo)
                    shutil.copy2(filePathOne, folderPathTwo)

                    log("", "", "", "", "", "", "CM", action)
                    changesMade += 1

                except:
                    log("", "", "", "", "", "", "NM", action)

        elif action == "A": #add a new folder in path2

            try:
                folderTwoPath = f2 + addition + "\\" + fileORfolder
                os.mkdir(folderTwoPath)

                log("", "", "", "", "", "", "CM", action)
                changesMade += 1
            
            except:
                log("", "", "", "", "", "", "NM", action)

        else:
            print("This should never execute, if it does there is a bug")
            
    else:
        #this can never execute unless mode is incorrectly set
        print("Please ensure that mode is set to 'action' or 'log in the config file.")
        pass
    
    #when copying, maybe check if direct parent folder exists.

def log(f1, f1N, f2, f2N, addition, fileORfolder, suggestedAction, action):
    global suggestedChanges
    global logFileName
    #parent1 and parent2 are the larger directories that lead to the file/folder

    # actions:
    # X - show title and configure log
    # S - Set up file
    # F - Finish - finish and give summary
    # P - calculating percentage
    # C - Copy 1 to 2 (when 2 does not exist)
    # R - Replace - delete 2 (when 1 is better state than 2) and copy 1 to 2
    # N - No action required
    # E - Error - first file/folder not found
    # A - Add a new folder
    # CM - change made
    # NM = change not made

    output = []
    action += " "

    if action[0] in actions and suggestedAction[0] in actions:

        if action == " " and mode == "action": #method of taking inputs when actionable
            if suggestedAction == "C" or suggestedAction == "R" or suggestedAction == "A" or suggestedAction == "N":

                if logfileLocation != "None":
                    logFileName = logfileLocation + "\\" + "syncLog " + str(datetime.datetime.now())[:10] + ".txt"
            
                    logFile = open(logFileName, "a+")
                else:
                    logFileName = "syncLog " + str(datetime.datetime.now())[:10] + ".txt"

                    logFile = open(logFileName, "a+")

                output = []
                line1 = "ACTION: "
                print(line1, end = "")

                action = str(input())
                action = action.upper()
                action += " "

                if action != "N ":
                    if action != "D ": #user can choose to delete a file
                        if action != suggestedAction + " ":
                            if action == " " or action == "Y ": #pressing enter goes with suggested action
                                action = suggestedAction + " "
                            else:
                                action = "N "

                line2 = "EXECUTE? "
                print(line2, end = "")
                
                response = str(input())
                response = response.lower()
                response += " "

                if response[0] != "y":
                    action = "N "

                action = action[:len(action)-1]
                line1 += action

                if action == "N":
                    line2 += response + " (No)"
                else:
                    line2 += response + " (Yes)"
                logFile.writelines(line1 + "\n")
                logFile.writelines(line2 + "\n")

                logFile.close()

        elif suggestedAction == "CM": #change made
            output = ["", ""]
            output[0] = "CHANGE MADE: " + action
            pass

        elif suggestedAction == "NM": #change not made
            output = ["", ""]
            output[0] = "CHANGE NOT MADE"
            pass

        elif suggestedAction == "X":
            output = ["", "", "", ""]
            output[0] = "============================================================================================================================================================"
            
            title = "LOG - " + str(datetime.datetime.now())[:19]
            output[2] = title

        
        elif suggestedAction  == "S":

            output  = ["", "", "", "", "", ""]
            output[0] = "============================================================================================================================================================"
            output[1] = "Syncing " + f1N + " to " + f2N
            output[2] = f1N + ": " + f1
            output[3] = f2N + ": " + f2
            output[4] = "=========================================================================================================="
        
        elif suggestedAction == "P":
            output = ["", ""]
            output[0] = "============================================================================================================================================================"
            output[1] = "Checking... (This may take a while)"
        
        elif suggestedAction == "F":
            output = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
            output[0] = "============================================================================================================================================================"
            title = "FINISHED - " + str(datetime.datetime.now())[:19]
            output[2] = title
            output[4] = "SUGGESTED CHANGES: " + str(suggestedChanges)
            output[5] = "CHANGES CARRIED OUT: " + str(changesMade)
            if logFileName[0] == "C":
                output[7] = "LOG FILE PATH: " + logFileName
            else:
                output[7] = "LOG FILE PATH: " + logfileLocation + "\\" + logFileName
            output[8] = "BIN FOLDER PATH: " + deletedfileLocation
            output[10] = "ESTIMATED PERCENTAGE SYNCED: " + str(percentageSynced) + "%"
            output[12] = "TIME TAKEN: " + str(elapsedTime) + " s" 
            output[14] = "============================================================================================================================================================"
            
        
        #if not actionable, no need to specify action, just specify suggested Action

        elif suggestedAction == "C":
            #when action is "N", does the logging
            #in execute action, if actionable, action is set to nothing and the action part is carried out

            #say that has copied

            suggestedChanges += 1


            output = ["", "", ""] #fileTwoPath = f2 + addition + "\\" + fileName
            output[0] = "SUGGESTED ACTION: " + suggestedAction + " - Copy " + f1N + " \"" + addition + "\\" + fileORfolder + "\" to " + f2N + " \"" + addition + "\""

            date1 = datetime.datetime.fromtimestamp(getDate(f1, addition, fileORfolder, compareDateParameter))
            fileSize1, unit1 = getSize(f1, addition, fileORfolder, "smallest")

            output[1] = f1N + " \"" + "\\" + fileORfolder + "\" - " + str(date1) + ", " + str(fileSize1) + " " + unit1
            output[2] = f2N + ": None - None, 0B"

            if mode != "action":
                output.append("")


        elif suggestedAction == "R":
            #say that has replaced 2 with 1

            suggestedChanges += 1

            output = ["", "", ""]
            output[0] = "SUGGESTED ACTION: " + suggestedAction + " - Replace " + f2N + " \"" + addition + "\\" + fileORfolder + "\" with " + f1N + " " + " \"" + addition + "\\" + fileORfolder + "\""

            date1 = str(datetime.datetime.fromtimestamp(getDate(f1, addition, fileORfolder, compareDateParameter)))[:16]
            date2 = str(datetime.datetime.fromtimestamp(getDate(f2, addition, fileORfolder, compareDateParameter)))[:16]

            fileSize1, unit1 = getSize(f1, addition, fileORfolder, "smallest")
            fileSize2, unit2 = getSize(f2, addition, fileORfolder, "smallest")

            output[1] = f1N + " \"" + "\\" + fileORfolder + "\" - " + str(date1) + ", " + str(fileSize1) + " " + unit1
            output[2] = f2N + " \"" + "\\" + fileORfolder + "\" - " + str(date2) + ", " + str(fileSize2) + " " + unit2

            if mode != "action":
                output.append("")


        elif suggestedAction == "N" and suggestedAction + " " != action:
            #say that no action is needed

            output = ["", "", ""]
            output[0] = "SUGGESTED ACTION: " + suggestedAction + " - No action is required" 

            date1 = str(datetime.datetime.fromtimestamp(getDate(f1, addition, fileORfolder, compareDateParameter)))[:16]
            date2 = str(datetime.datetime.fromtimestamp(getDate(f2, addition, fileORfolder, compareDateParameter)))[:16]

            fileSize1, unit1 = getSize(f1, addition, fileORfolder, "smallest")
            fileSize2, unit2 = getSize(f2, addition, fileORfolder, "smallest")

            output[1] = f1N + " \"" + "\\" + fileORfolder + "\" - " + str(date1) + ", " + str(fileSize1) + " " + unit1
            output[2] = f2N + " \"" + "\\" + fileORfolder + "\" - " + str(date2) + ", " + str(fileSize2) + " " + unit2

            if mode != "action":
                output.append("")
            

        elif suggestedAction == "E" and logErrorNoFolderOne == True:
            #say that first file was not found
            output = ["", "", ""]
            output[0] = "SUGGESTED ACTION: " + suggestedAction + " - No action is required"

            output[1] = f1N + " \"" + "\\" + fileORfolder + "\" - Does not exist in " + addition
            output[2] = f2N + " \"" + "\\" + fileORfolder + "\" - Existence is not measured"

            if mode != "action":
                output.append("")

        elif suggestedAction == "A":
            #say that a new folder had to be added

            suggestedChanges += 1

            output = ["", "", ""]

            output[0] = "SUGGESTED ACTION: " + suggestedAction + " - Add new folder \"" + fileORfolder + "\" in " + f2N + ": " + addition

            output[1] = f1N + " \"" + "\\" + fileORfolder + "\" - " + "Exists in " + f1N + ": " + addition
            output[2] = f2N + " \"" + "\\" + fileORfolder + "\" - " + "Does not exist in " + f2N + ": " +  addition

            if mode != "action":
                output.append("")

        else:
            
            pass
        
        if output != []:
            
            if logfileLocation != "None":
                logFileName = logfileLocation + "\\" + "syncLog " + str(datetime.datetime.now())[:10] + ".txt"
            
                logFile = open(logFileName, "a+")
            else:
                logFileName = "syncLog " + str(datetime.datetime.now())[:10] + ".txt"

                logFile = open(logFileName, "a+")


            for line in output:
                print(line)
                logFile.writelines(line + "\n")

            logFile.close()
        return action

def EvalExecLogFile(f1, f1N, f2, f2N, addition, fileName):
    evalActionFile(f1, f1N, f2, f2N, addition, fileName)

def EvalExecLogFolder(f1, f1N, f2, f2N, addition, folderName):
    evalActionFolder(f1, f1N, f2, f2N, addition, folderName)


def syncFolders(f1, f1N, f2, f2N):
    #f1 and f2 stands for the different directories that should match
    #f1 is primary and all content in it will be copied to f2
    x = log(f1, f1N, f2, f2N, "", "", "S", "S")
    
    for dirPath, dirNames, fileNames in os.walk(f1):


        for dirName in dirNames:

            addition = findNotCommon(f1, dirPath)

            # folderOnePath = f1 + addition + "\\" + dirName
            # parentOnePath = f1 + addition

            EvalExecLogFolder(f1, f1N, f2, f2N, addition, dirName)


        for fileName in fileNames:

            addition = findNotCommon(f1, dirPath)

            EvalExecLogFile(f1, f1N, f2, f2N, addition, fileName)



getConfig()
x = log("", "", "", "", "", "", "X", "X")
if calcPercentage == True:
    totalChecks = 0
    totalDifferences = 0


syncFolders(folderOne, folderOneName, folderTwo, folderTwoName)
syncFolders(folderTwo, folderTwoName, folderOne, folderOneName)

if calcPercentage == True:
    percentageSynced = 100 - ((totalDifferences/totalChecks)*100)
    percentageSynced = f"{percentageSynced:.5f}"
else:
    percentageSynced = "n/a"

endTime = time.time()
elapsedTime = endTime-startTime
elapsedTime = f"{elapsedTime:.2f}"

x = log("", "", "", "", "", "", "F", "F")