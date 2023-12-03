# File-Syncer
A program that syncs to folders to each other and has various safety measures and statistic trackers.

# Using sync_files.py or sync_files.exe
This is the main program. Before running, ensure that you correctly configure the sync_config.ini file.

In action mode, to make changes you will need to respond in the terminal/console. Input a single letter when asked what action to carry out. Input yes or no when asking if the program should execute this action.

Note: The double negative results in no action being taken

    ACTION: N
    EXECUTE: no
    CHANGES NOT MADE

Possible Actions are as follows:

    N - do Nothing
    C - Copy file1 to path2 (this is recommended when file2 does not exist)
    R - Replace file2 with file1 (this is recommended when file1 is newer/better version than file2)
    A - Add a new folder in path2 in accordance with the folder in path1
    D - Delete the first folder/file (used when one copy of a file has been deliberately deleted by the user and the same is wished
        to be done to the other file)

# sync_config.ini
See the configuration file for information on how and what to input as configurations.

Quotation marks should not be used. For boolean variables, 0 and 1 are required.

I have included date parameters other than last modified in the code for reusability, but as I have not use for these, I have not had a chance to test them.

# Outline on how the code works

The code recursively moves through the first path's directory, comparing each folder and file to its correspondent in the second path's directory. 

After each file/folder that it suggests an action for, it amends the log. 

It generates the action from the existance of both files/folders, file size, and the date parameter as specified in the configuration file. 

Once finished, it repeats this process but referencing the second path's directory. This ensures that all files are synced from the first path's directory to the second's and vice versa.

When in action mode, after each significant suggested action, it checks with the user what to do when a confirmation is necessary.

When it has gone through both directories, it details the stats of the sync. These include the number of suggested changes, the changes carried out, the estimated percentage synced and the total time taken. Here is an example of that:

        ==========================================================================================================================

        FINISHED - 2023-12-03 21:48:54

        SUGGESTED CHANGES: 14
        CHANGES CARRIED OUT: 11

        LOG FILE PATH: [full path to log file that can be copied]
        BIN FOLDER PATH: [full path to Bin folder that can be copied]

        ESTIMATED PERCENTAGE SYNCED: 99.99397%

        TIME TAKEN: 41.37 s

        ==========================================================================================================================



# Warnings
Although I have thoroughly tested this code on my folders and files as well as specific set up conditions, there is no guarantee that it will not have errors when faced with other configurations of files and folders.

I have not tested date parameters other than last modified, so I can neither justify that they would be useful, nor say that they are bug free. Therefore, use these with caution.

Personal use of this program is carried out at your own risk. I cannot accept any responsibilty for unforeseen bugs.

# Copyright Information
I have not included a license on this program and associated configuration files. By default, this creative work is under exclusive copyright. This means that no one can copy, distribute, or modify your work without being at risk of take-downs, shake-downs, or litigation.

However, this program can be used for personal usage only. This means that as long as you do not copy/distribute/modify this program without my authorisation, you may use this for yourself.

Read more about program code that has no license here: https://choosealicense.com/no-permission/

