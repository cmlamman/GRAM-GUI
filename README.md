# GRAM
This is a GUI for inspecting Robo-AO observations and identifying potential companions within them. The program takes in observations pre-processed by the automated Robo-AO pipeline and allows the user to visually check data quality, telescope pointing and if the correct star was reduced. Users can also identify and save the location of companion stars, add a variety of tags to the observation, and enter a custom note. A text file of each observation's information is created, which can be compiled into an ensemble file. For more incormation see [Lamman et al. 2020].

# Usage
1. Make sure you have the following modules installed: Tkinter, numpy, matplotlib, astropy, shutil, glob, re, urllib, PIL, os, sys. This code is also written in Python 2.7 (sorry).

2. Run **preGUI.py** to create the images used in GRAM. This will prompt you for the path to target directories resulting from the automated Robo-AO pipeline. They should contain the 100p.fits stacked image, contrast curve, and psf-subbed image. This will create a new directory, **PreGUI** which contains all the information needed to run GRAM.

3. Run **runGUI.py**. This will prompt you for the path to the directiories you just created, and the program number. The GUI should then pop up. See below for detailed information on using the GUI itself.

4. As soon as you view a target in GRAM, a new text file is created in its 'preGUI' directory, called **guiOut.txt**. If you view the target again through GRAM and select something new or different this file will automatically update. You can combine all guiOut files using **combine_guiOut.py**, which will again prompt you for the path to the "preGUI" target directories and the program number, in addition to your name. For the key to reading the guiOut files see below.

# The GRAM interface

Navigation:
- Keys: left/right arrow keys or space bar to progress one at a time, Ctrl+left/right arrow keys progresses through 50 targets at a time
- Buttons: < or > to progress one at a time, << or >> to progress 10 at a time

Quality Check:
- Each target is tagged 'good' as default. Selecting 'good', 'uncertain', or 'bad' will overwrite other tags. 

Ensuring correct target was reduced:
- Bottom left image is from DSS database, the Robo-AO field size is marked in faint brown box. Smaller green-outlined image is data, full field (35.6"). Presumed target location is marked in green. If this matches DSS image do nothing. If not, click on target and green circle will appear. Each time this position is re-selected it will overwrite previous position. Can also tag image for not enough stars or bad pointing. Reseting location undoes all location selections.

Companion:
- If no companion do nothing. Choose location of companion by clicking on the companion in any of the four bottom imags. For distant compaion, click in upper right image (8" across). Selecitons in close and far field are both saved and updated with new clicks. Resetting removes tags and clicked locations.

Notes Entry:
- Add any text note with no spaces or commas, press enter to save. Each time enter is pressed target's text file will be appended with note.


# Reading guiOut Files
- G: good
- U: uncertain
- B: bad
- NES: not enough stars
- INP: incorecct pointing
- DDB: needs different database
- CB: possible Close Binary
- NM: needs to be looked at manually
- Location: pixel coordinates of corrected target location
- Companion: pixel coordinates of companion within 1.75"
- Far Companion: pixel corrdinates companion within 4"


For Questions: Claire Lamman, claire.lamman@cfa.harvard.edu
