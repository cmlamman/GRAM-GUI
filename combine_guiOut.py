'''
TO COMBINE INDIVIDUAL TEXT FILES CREATED FROM 'runGUI.py'

Returns: One text file with info for each target located in directory containing individual target directories

Each time this program is run with the same name, new results are appended to old file. To make a different 
file enter a different name.
'''
import os
path = raw_input('Enter path to data directory (Ex- C:/Users/Claire/Robo-AO/Data/):') #prompt user for directory path
programnum = raw_input('Enter Program Number (Ex- 3):')                               #prompt user for program number
usersName = raw_input('Your name?')                                          #to seperate files created by different people

#Create 'Blank' Out File
if os.path.isfile(path+'/guiOutCombined_'+usersName+'.txt')==False:     #only create file if one doesn't already exist
    guiOutc = open(path+'/guiOutCombined_'+usersName+'.txt', 'w+')      #open/create blank file
    guiOutc.write('TARGET| G | U | B |NES|INP |DDB|CB |NM |\
        Location | Companion | Far Companion ')                         #Text file header
    guiOutc.close()                                                     #close file or face programer exile
    
#Go Through Every Target Directory in Given Directory    
for b in [s for s in os.listdir(path) if s.startswith(programnum)]:
    
    #Read Target's file into list    
    with open(path+b+'/guiOut.txt', 'r') as infile:
        lines = infile.read().split('\n')                               #create list of target's info, each line an entry
        #create a list of target info, taking out labels for each line (line 12 is for special notes and will often be blank)
        tags = ['\n', lines[0].strip('Target:')+',', lines[1].strip('G:')+',', lines[2].strip('U:')+',', lines[3].strip('B:')+',',\
                lines[4].strip('NES:')+',', lines[5].strip('INP:')+',', lines[6].strip('DDB:')+',', lines[7].strip('CB:')+',', lines[8].strip('NM:')+',',\
                lines[9].strip('Location:')+',', lines[10].strip('Companion:')+',',lines[11].strip('Far Companion:')+lines[12]]

    #Add info to combined text file
    with open(path+'/guiOutCombined_'+usersName+'.txt', 'a') as f:
        for line in tags:
            f.write(line)
