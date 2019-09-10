import Tkinter as tk

from Tkinter import *

from PIL import Image, ImageTk

import glob, sys, os

import numpy as np





#FILE PATHS, TARGET NAMES & INFO

path = raw_input('Enter path to data directory (Ex- C:/Users/Claire/RoboAO/Data/):') #prompt user for directory path

programnum = raw_input('Enter Program Number (Ex- 3):')                               #prompt user for program number

dpath = sorted(glob.glob(path+programnum+'_*'))                           #target directories

nlist = [s for s in os.listdir(path) if s.startswith(programnum+'_')]                     #make list of directory path  

names = [i.split(".")[0] for i in (nlist[0::1])]                #Create list of object names



def convertCoords(xo, yo, pngDim, pngArcsec, xoff, yoff):

    '''

    Convert coordinates on a Tkinter canvas to cooresponding fits pixel coordinates for a specific target

    ----------------

    INPUT PARAMETERS

    xo, yo = original coordinates on canvas, relative to upper left corner, int

    pngDim = dimmensions of square Tkinter canvas, int

    pngArcsec = arcsecond across image displayed on square canvas, int

    xoff, yoff = target's offset from center of original fits image, in pixels, int

    '''

    cx = (xo-(pngDim/2.))*(pngArcsec/pngDim)        #Coordinates relative to center of png in arc seconds

    cy = ((pngDim/2.)-yo)*(pngArcsec/pngDim)

    dx = cx*(1000./17.4)                            #Pixel coordinates relative to target in 2048x2048 image

    dy = cy*(1000./17.4)                            #...17.4 miliarcsec/pixel

    fx = dx+xoff+1024                               #pixel coordinates in original fits file relative to lower left corner

    fy = dy+yoff+1024                               #...and offset by target's offset from center

    return fx, fy





class MyApp(object):
    """GUI to view, tag, and select various locations for data of multiple roboao targets"""
    def __init__(self, root):
        root = Toplevel()                           #Toplevel, not Tk to make python happy
        root.wm_title("Target Examination")         #Window Title
        root.configure(background='black')          #black background
        root.geometry('{}x{}'.format(1300, 750))    #sixe of window      
        self.buttonframe = Frame(root, bd=1)        #use grids to controll label positions
        self.buttonframe.grid(row=8, column=20)
        
        #FRAME FOR CANVASES
        #position selector
        frame1 = Frame(root, highlightbackground="DarkOliveGreen4", highlightthickness=2, width=200, height=200) #frame color, size
        frame1.grid(row=6, column=4, rowspan=3, padx=20, pady=30, sticky=NW)                            #location on grid, space in y direction
        frame1.pack_propagate(False)
        
        #close companion selector
        frame2 = Frame(root, highlightbackground="cadet blue", highlightthickness=2, width=900, height=225) #frame color, size
        frame2.grid(row=9, column=4, rowspan=1, columnspan=50, sticky=NE)   #location on grid, spans columns, stuck to East
        frame2.pack_propagate(False)
        
        #far companion selector
        frame3 = Frame(root, highlightbackground="cadet blue", highlightthickness=2, width=400, height=400) #frame color, size
        frame3.grid(row=1, column=7, rowspan=7, columnspan=1, padx=20, sticky=S)    #location on grid, y space, stuck to West
        frame3.pack_propagate(False)
        
        root.bind('<Return>', self.enterKey)
        root.bind('<Left>', self.leftKey)               #Bind arrow and space bar keys for moving through targets           
        root.bind('<Right>', self.rightKey)
        root.bind('<space>', self.spaceKey)
        root.bind('<Control-Left>', self.ctrleft)
        root.bind('<Control-Right>', self.ctright)
        root.protocol("WM_DELETE_WINDOW", on_closing)   #If window closes shut everything down
        
        com0=[500]*(len(names)*2)                     #for saving circle coordinates
        com1=[1000]*(len(names)*2)
        com2=[500]*(len(names)*2)
        
        global ct           #declare global variable
        ct=-1               #start with -1 so becomes 0 when function is called upon gui opening
        global nxtTarget    
        def nxtTarget(f):   #Function to bring up individual information for each target
            global ct       #redefine ct globally each time function is called
            ct+=f
            
            if (ct+1)>len(names):               #Close window if there are no more targets
                on_closing()

            Label(root, text='no spaces, [Enter] to save', fg='dim gray', bg='black', font=("Helvetica", 8)).grid(row=7, column=6, sticky=SW, pady=20)
            global e1
            e1=Entry(root, width=25)
            e1.grid(row=7, column=6, sticky=SW)
            
            canvas1.coords(circle0, com0[ct*2]-8, com0[(ct*2)+1]-8, com0[ct*2]+8, com0[(ct*2)+1]+8,)   #update circle positions
            canvas2.coords(circle1, com1[ct*2]-8, com1[(ct*2)+1]-8, com1[ct*2]+8, com1[(ct*2)+1]+8)
            canvas2.coords(circle2, com1[ct*2]+225-8, com1[(ct*2)+1]-8, com1[ct*2]+225+8, com1[(ct*2)+1]+8)
            canvas2.coords(circle3, com1[ct*2]+450-8, com1[(ct*2)+1]-8, com1[ct*2]+450+8, com1[(ct*2)+1]+8)
            canvas2.coords(circle4, com1[ct*2]+675-8, com1[(ct*2)+1]-8, com1[ct*2]+675+8, com1[(ct*2)+1]+8)
            canvas3.coords(circle5, com2[ct*2]-8, com2[(ct*2)+1]-8, com2[ct*2]+8, com2[(ct*2)+1]+8)
            
      
            #OPEN FILES
            inf=[]
            tinf = open(dpath[ct]+'/info4GUI.txt', 'r').readlines()   #target info
            for t in tinf:
                inf.extend([float(t.strip('\n'))])                       
            
            ftsim = sorted(glob.glob(dpath[ct]+'/*.png'))                         #all png image
            xpix = inf[1]                                  #get pixel coordinates of target
            ypix = inf[0]
            global xoffset
            xoffset = xpix-1024                                                  #target position relative to center of fits
            global yoffset
            yoffset = ypix-1024
            
            #CREATE TEXT FILE TO STORE RESULTS
            if os.path.isfile(dpath[ct]+'/guiOut.txt')==False:                  #only create file if one doesn't already exist
                guiOut = open(dpath[ct]+'/guiOut.txt', 'w+')                                                    #open/create blank file
                guiOut.write("%s \n%s \n%s \n%s \n%s \n%s \n%s \n%s \n%s \n%s \n%s \n%s \n" % ('Target:'+names[ct],       #create blank template    
                    'G:x', 'U:-', 'B:-', 'NES:-', 'IP:-', 'DDB:-', 'CB:-', 'NM:-', 'Location:-', 'Companion:-', 'Far Companion:-'))
                guiOut.close()                                                                                  #close file
            
            tinfr = []                                      #Blank array to store target info
            for i in tinf:
                if i != tinf[-1]:                           #Ignore last item in list: 'OK'
                    tinfr.append(str(round(float(i), 2)))   #round to two sf, convert back to string

        
            #SET UP WINDOW
            #Target Info
            Label(root, text=names[ct], fg='white', bg='black', font=("Helvetica", 16))\
                  .grid(row=0, column=0, columnspan=10, sticky=W)    #target name (color, font, location)
            Label(root, text='Core: '+str(inf[2])+'     Halo: '+str(inf[3])+'     Strehl: '+str(inf[4])+'%     Mag: '+str(inf[5]),\
                  fg='white', bg='black', font=('Helvetica', 12))\
            .grid(row=1, column=0, columnspan=4, sticky=W)          #target information (color, font, location)
            Label(root, text='Displaying Target  '+str(ct+1)+'/'+str(len(names)), fg='white', bg='black', font=('Helvetica', 12))\
            .grid(row=0, column=7, padx=20, sticky=E)                        #status on total targets, current/total (color, font, location)
        
            #Set up Images
            photo2 = ImageTk.PhotoImage((Image.open(ftsim[0])).resize((250, 150), Image.ANTIALIAS)) #contrast curve
            photo4 = ImageTk.PhotoImage((Image.open(ftsim[3])).resize((200, 200), Image.ANTIALIAS)) #full field image
            photo5 = ImageTk.PhotoImage((Image.open(ftsim[4])).resize((375, 375), Image.ANTIALIAS)) #database field
            photo6 = ImageTk.PhotoImage((Image.open(ftsim[1])).resize((900, 225), Image.ANTIALIAS)) #fits collage
            photo7 = ImageTk.PhotoImage((Image.open(ftsim[2])).resize((400, 400), Image.ANTIALIAS)) #larger field for companion

            label2 = Label(root, image=photo2)                          #create labels from the 2 images not displayed on a canvas
            label5 = Label(root, image=photo5, bg='DarkOliveGreen4')    #This one with a green border
            label2.image = photo2                                       #keep a reference!
            label5.image = photo5
            label2.grid(row=2, column=0, rowspan=4, padx=10, sticky=N)                     #contrast curve location
            label5.grid(row=6, column=0, rowspan=4, columnspan=4, pady=30, sticky=N) #database image location
           
            #Update previously created three canvases with images for new target
            photo4.image=photo4                     #full field image
            canvas1.itemconfig(img1, image=photo4)  
            photo6.image=photo6                     #fits collage
            canvas2.itemconfig(img2, image=photo6)
            photo7.image=photo7                     #larger field for companion
            canvas3.itemconfig(img3, image=photo7)
      
        def selectloc1(event):                                                     
            '''For Location Check: save cursor position and place circle on mouse release'''
            x, y = event.x, event.y                                             #save mouse coordinates on canvas
            canvas1.coords(circle0, x-8, y-8, x+8, y+8)                         #cirlce around selected location
            fx, fy = convertCoords(x, y, 200., 35.6352, 0, 0)                   #convert to pixel coordinates
            editOut(9, 'Location: ('+str(fx)+' '+str(fy)+')')
            com0[ct*2], com0[(ct*2)+1] = x, y                                   #save circle location

        
        def selectloc2(event):
            '''For Close Companion Location: save cursor position and place circle on each of 4 images''' 
            x, y = event.x, event.y                                             #save mouse coordinates on canvas
            #To account for user not clicking in left most image
            imcl = 225.      #lendth of one image in canvas
            if (x-imcl)<0:        #if click is in first image
                x-=0
            elif (x-(imcl*2.))<0: #if click is in second image...
                x-=imcl           #subtract 1 image length
            elif (x-(imcl*3.))<0: #if click is in third image...
                x-=(imcl*2.)      #subtract 2 image lengths
            elif (x-(imcl*4.))<0: #if click is in fourth image...
                x-=(imcl*3.)      #subtract 3 image lengths
            canvas2.coords(circle1, x-8, y-8, x+8, y+8)                         #circle around selected location for each image
            canvas2.coords(circle2, x+225-8, y-8, x+225+8, y+8)
            canvas2.coords(circle3, x+450-8, y-8, x+450+8, y+8)
            canvas2.coords(circle4, x+675-8, y-8, x+675+8, y+8)
            fx, fy = convertCoords(x, y, 225., 1.5, xoffset, yoffset)            #convert to pixel coordinates
            editOut(10, 'Companion: ('+str(fx)+' '+str(fy)+')')                  #update out text file
            com1[ct*2], com1[(ct*2)+1] = x, y                                    #save circle location
            
        def selectloc3(event):
            '''For Far Companion Location: save cursor position and place circle on mouse release'''
            x, y = event.x, event.y                                             #save mouse corrdinates on canvas
            canvas3.coords(circle5, x-8, y-8, x+8, y+8)                         #circle around selected location
            fx, fy = convertCoords(x, y, 400., 8., xoffset, yoffset)            #convert to pixel coordinates
            editOut(11, 'Far Companion: ('+str(fx)+' '+str(fy)+')')             #update out text file
            com2[ct*2], com2[(ct*2)+1] = x, y                                   #save circle location
        
        def editOut(line, mrk):
            '''Function to replace specific line in results file with given string'''
            with open(dpath[ct]+'/guiOut.txt', 'r') as file:
                data = file.readlines()                                         #read list of lines into data
            data[line] = mrk+'\n'                                               #replace line with new entry and end that line
            with open(dpath[ct]+'/guiOut.txt', 'w') as file:
                file.writelines(data)                                           #rewrite out file
        
        def rmCircle(circlenum):
            '''Remove previously placed circle from view in canvas'''
            if circlenum==0:                                                    #circle for location selection
                com0[ct*2], com0[(ct*2)+1] = 500, 501
            if circlenum==1:                                                    #circles for companion selection
                com1[ct*2], com1[(ct*2)+1] = 5000, 5001
                com2[ct*2], com2[(ct*2)+1] = 5000, 5001
            canvas1.coords(circle0, com0[ct*2]-8, com0[(ct*2)+1]-8, com0[ct*2]+8, com0[(ct*2)+1]+8,)   #update circle positions
            canvas2.coords(circle1, com1[ct*2]-8, com1[(ct*2)+1]-8, com1[ct*2]+8, com1[(ct*2)+1]+8)
            canvas2.coords(circle2, com1[ct*2]+225-8, com1[(ct*2)+1]-8, com1[ct*2]+225+8, com1[(ct*2)+1]+8)
            canvas2.coords(circle3, com1[ct*2]+450-8, com1[(ct*2)+1]-8, com1[ct*2]+450+8, com1[(ct*2)+1]+8)
            canvas2.coords(circle4, com1[ct*2]+675-8, com1[(ct*2)+1]-8, com1[ct*2]+675+8, com1[(ct*2)+1]+8)
            canvas3.coords(circle5, com2[ct*2]-8, com2[(ct*2)+1]-8, com2[ct*2]+8, com2[(ct*2)+1]+8)
        
        def sequence(*functions):
            '''Funciton to combine multiple functions (so buttons can have multiple commands)'''
            def func(*args, **kwargs):                                          
                return_value = None
                for function in functions:
                    return_value = function(*args, **kwargs)
                return return_value
            return func
        
        global save_note
        def save_note():
            '''function to append note to targets text file'''
            with open(dpath[ct]+'/guiOut.txt', 'a') as file:
                file.write(', Note: %s' % (e1.get())) 
        
        #CANVASES FOR POSITION SELECTION
        #Position Check
        canvas1 = Canvas(frame1, width=200, height=200, highlightthickness=0, cursor='@arrow.cur')  #create canvas, size, cursor
        canvas1.pack(expand = YES, fill = BOTH)
        img1 = canvas1.create_image(0, 0, anchor=NW)                                    #give canvas no image initially
        circle0 = canvas1.create_oval(500, 500, 501, 501, outline='chartreuse2')        #create out-of-sight circle
        canvas1.bind("<ButtonPress-1>", selectloc1)                                     #if click here, call selectloc1 function
        
        canvas2 = Canvas(frame2, width=900, height=225, highlightthickness=0, cursor='@arrow.cur')  #canvas frame, size, cursor
        canvas2.pack(expand = YES, fill = BOTH)
        img2 = canvas2.create_image(0, 0, anchor=NW)                                    #no initial image
        circle1 = canvas2.create_oval(500, 500, 501, 501, outline='chartreuse2')        #create out-of-sight circle for each image
        circle2 = canvas2.create_oval(500, 500, 501, 501, outline='chartreuse2')
        circle3 = canvas2.create_oval(500, 500, 501, 501, outline='chartreuse2')
        circle4 = canvas2.create_oval(500, 500, 501, 501, outline='black')
        canvas2.bind("<ButtonPress-1>", selectloc2)                                     #if click here, call selectloc2 function
        
        canvas3 = Canvas(frame3, width=400, height=400, highlightthickness=0, cursor='@arrow.cur')  #canvas frame, location, cursor
        canvas3.pack(expand = YES, fill = BOTH)
        img3 = canvas3.create_image(0, 0, anchor=NW)                                    #set up for but don't include image yet
        circle5 = canvas3.create_oval(500, 500, 501, 501, outline='black')        #create out-of-sight circle
        canvas3.bind("<ButtonPress-1>", selectloc3)                                     #if click here, call selectloc3 function
        
        canvas3.create_oval(0, 0, 400, 400, outline='white')
        
        #LABELS AND BUTTONS
        #Input Field for Notes
        Label(root, text="Note:", fg='white', bg='black', font=("Helvetica", 12)).grid(row=7, column=6, sticky=SW, pady=35)
        #Quality Check Label
        Label(root, text='QUALITY CHECK', fg='white', bg='black', font=("Helvetica", 12, 'bold'))\
            .grid(row=2, column=1, columnspan=3, padx=15, sticky=N) #location on grid
        #Location Label
        Label(root, text='LOCATION', fg='DarkOliveGreen4', bg='black', font=("Helvetica", 12, 'bold'))\
            .grid(row=2, column=4, sticky=N)
        #Companion Label
        Label(root, text='COMPANION', fg='cadet blue', bg='black', font=("Helvetica", 12, 'bold'))\
            .grid(row=2, column=6, padx=10, sticky=N)
        #Image Labels
        Label(root, text='DSS Database Image', fg='DarkOliveGreen4', bg='black', font=('Helvetica', 8))\
            .grid(row=9, column=0, sticky=SW, padx=35, pady=55)                        #Database iamge label
        Label(root, text='Full Field Fits                            N ^    E ->', fg='DarkOliveGreen4', bg='black', font=('Helvetica', 8))\
            .grid(row=8, column=4, sticky=NW, padx=20, pady=10)                        #Full field
        Label(root, text='Field = 1.5" across', fg='cadet blue', bg='black', font=('Helvetica', 8))\
            .grid(row=9, column=4, sticky=SW, padx=10)                        #Full field
        Label(root, text='Field = 8" across', fg='cadet blue', bg='black', font=('Helvetica', 8))\
            .grid(row=8, column=7, sticky=NW, padx=30)                        #Full field
            
        #Button, name, command, size, color, .position
        G = Button(root, text = u'\u2713', command=lambda: sequence(editOut(1,'G:x'), editOut(2,'U:-'), editOut(3, 'B:-')),\
              height=1, width=3, bg='chartreuse4', font=('Helvetica', 12)).grid(row=3, column=1, sticky=N)            #good
        U = Button(root, text="?", command=lambda: sequence(editOut(1,'G:-'), editOut(2,'U:x'), editOut(3, 'B:-')),\
              height=1, width=3, bg='gold3', font=('Helvetica', 12, 'bold')).grid(row=3, column=2, sticky=N)                     #unsure
        B = Button(root, text="X", command=lambda: sequence(editOut(1,'G:-'), editOut(2,'U:-'), editOut(3, 'B:x')),\
              height=1, width=3, bg='IndianRed4', font=('Helvetica', 12, 'bold')).grid(row=3, column=3, sticky=N) #bad
        Bck = Button(root, text="<", command=lambda: nxtTarget(-1), height=1, width=2, bg='grey',\
              font=('Helvetica', 12, 'bold')).grid(row=4, column=1, sticky=NE) #back
        Nxt = Button(root, text=">", command=lambda: nxtTarget(1), height=1, width=2, bg='grey',\
              font=('Helvetica', 12, 'bold')).grid(row=4, column=3, sticky=NW) #next
        FBW = Button(root, text="<<", command=lambda: nxtTarget(-10), height=1, width=2, bg='grey',\
              font=('Helvetica', 12, 'bold')).grid(row=5, column=1, sticky=NE) #fast-backwards
        FFW = Button(root, text=">>", command=lambda: nxtTarget(10), height=1, width=2, bg='grey',\
              font=('Helvetica', 12, 'bold')).grid(row=5, column=3, sticky=NW) #fast-forward
        NES = Button(root, text="Not Enough Stars", command=lambda: editOut(4, 'NES:x'), height=1, width=15, bg='DarkOliveGreen4',\
              font=('Helvetica', 12)).grid(row=3, column=4, padx=20, sticky=N)            #not enought stars
        INP = Button(root, text="Incorrect Pointing", command=lambda: editOut(5, 'INP:x'), height=1, width=15, bg='DarkOliveGreen4',\
              font=('Helvetica', 12)).grid(row=4, column=4, padx=20, sticky=N)  #incorrect pointing
        DDB = Button(root, text="Needs diff Database", command=lambda: editOut(6, 'DDB:x'), height=1, width=15, bg='DarkOliveGreen4',\
              font=('Helvetica', 12)).grid(row=5, column=4, sticky=N, padx=20)  #Needs different database
        LOk = Button(root, text = 'Reset Location', command=lambda: sequence(editOut(9, 'Location:-'), rmCircle(0), editOut(5, 'INP:-'), editOut(4, 'NES:-'), editOut(6, 'DDB:-')),\
              height=1, width=15, fg='DarkOliveGreen4', bg='gray25', font=('Helvetica', 12)).grid(row=7, column=6, sticky=NW)  #location is OK
        NC = Button(root, text="Reset Companion", command=lambda: sequence(editOut(10, 'Companion:-'), editOut(11, 'Far Companion:-'), rmCircle(1), editOut(7, 'CB:-'), editOut(8, 'NM:-')),\
              height=1, width=15, fg='cadet blue', bg='gray25', font=('Helvetica', 12)).grid(row=7, column=6, pady=40, sticky=NW)  #no companion
        CB = Button(root, text="Poss. Close Binary", command=lambda: editOut(7, 'CB:x'),\
              height=1, width=15, bg='cadet blue', font=('Helvetica', 12)).grid(row=3, column=6, sticky=NW)  #possible close binary
        NM = Button(root, text="Look at Manually", command=lambda: editOut(8, 'NM:x'),\
              height=1, width=15, bg='cadet blue', font=('Helvetica', 12)).grid(row=4, column=6, sticky=NW)  #no companion
        
        nxtTarget(1) #Star GUI with first target
            
    @staticmethod           #use static function so can be called by all classes
    def enterKey(event):     #if press left arrow key, go back one target
        save_note()
    
    @staticmethod           #use static function so can be called by all classes
    def leftKey(event):     #if press left arrow key, go back one target
        nxtTarget(-1)
        
    @staticmethod
    def rightKey(event):    #if press right arrow key, go to next target
        nxtTarget(1)
        
    @staticmethod
    def spaceKey(event):    #if press space bar, go to next target
        nxtTarget(1)
        
    @staticmethod
    def ctrleft(event):    #if press space bar, go to next target
        nxtTarget(-50)
        
    @staticmethod
    def ctright(event):    #if press space bar, go to next target
        nxtTarget(50)
    
def on_closing():       #If window closes shut everything down
    root.destroy()      #Kill GUI
    sys.exit()          #shut down (might make python angry, can be removed)
            
        
root = Tk()
root.withdraw()   #stop extra window from appearing
MyApp(root)       
root.title('Tkinter Widgets')
root.mainloop()
