import matplotlib
matplotlib.use('agg')

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from shutil import copyfile
import glob, re, urllib, PIL, os, astropy.stats
from PIL import Image, ImageDraw


#path to data directories containing 'source data' from online database for each target
pa = raw_input('Enter path to data directory (Ex- C:/Users/Claire/RoboAO/Data/):')
programnum = raw_input('Enter Program Number (Ex- 3):') 
path = pa+programnum+'_*'
nwfl = pa+'preGUI'
nlist = [s for s in os.listdir(pa) if s.startswith(programnum+'_')]                      #make list of directory path  
names = sorted([i.split(".")[0] for i in (nlist[0::1])])                #Create list of object names


cct = 0.10                                                            #core cut
if not os.path.exists(nwfl):
    os.mkdir(nwfl)
arcssp = 1.5                                                        #arc seconds across total image for fits collage
sp = arcssp*(1000./(17.4*2.))                                       #converting arcsec to pixels on either side of target
trgtlst = sorted(glob.glob(path))
k=0                                                                 #Make sure all plots are seperate
m=1                                                                 #keep track of loop
for j in trgtlst:                                                   #loop over every target directory
    
    print 'Working on: ' + j.split("/")[-1]+',  '+str(m)+'/'+str(len(trgtlst))   #print current target and progress
    
    #ONLY LOOK AT OBJECTS WITH CORE >= 0.1
    stinfo = sorted(glob.glob(j + '/automated/strehl/*.txt'))
    with open(stinfo[0], 'r') as st:
        tinf = st.readlines()[1].split()            #target info

    if float(tinf[2])>=cct:
        ntd = nwfl+'/'+names[m-1]                      #new target directory
        if not os.path.exists(ntd):
            os.mkdir(ntd)
        print j.split("/")[-1]+' has passed cut'
        
    if float(tinf[2])<cct:
        m+=1
        continue
    
    #LOADING FILES
    fts = j+'/automated/100p.fits'                                          #100p fits file
    ftsim= fits.getdata(fts)                                                #load fits file and store as array
    old = np.seterr(invalid='ignore')                                       #ignore invalid values for taking log in next line
    ftslg = np.log(ftsim+.4)                                                #for log plots
    ftslgn = np.log(ftsim+50)
    np.seterr(**old)                                                        #restore settings to not ignore invalid values
    psf = fits.getdata((sorted(glob.glob(j+'/automated/pca/*.fits')))[0])   #load psf fits file and store as array
    
    contcurv = sorted(glob.glob(j+'/automated/pca/*curve.png'))
    copyfile(contcurv[0], ntd+'/contrast_curve.png')
    
    #CREATE ONE TEXT FILE FOR GUI
    tinfr = []                                      #Blank array to store target info
    for i in tinf:
        if i != tinf[-1] and i != tinf[-2]:         #Remove tag and FWHM, last two items in strehl txt
            tinfr.append(round(float(i), 2))        #round to two sf, convert back to string
    hdulist = fits.open(fts)
    tinfr.append(hdulist[0].header['MAGNITUD'])     #Get object magnitude from header
    np.savetxt(ntd+'/info4GUI.txt', tinfr)
    
    xpix = int(tinfr[1])                            #get pixel coordinates of target
    ypix = int(tinfr[0])
    xpsf = 100                                      #pixel coordinates of target for psf images
    ypsf = 100                                      #..since psf has target centered
        
    #PNG FROM FITS FOR POSITION FINDER    
    fig = plt.figure(k, frameon=False)
    fig.set_size_inches(10,10)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.imshow(ftslg, cmap='gray', vmin=-2.e0, vmax=2.e0)               #log plot, vmin and max to adjust scaling
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.plot(xpix-220, ypix, 's', marker='_', mew=4, ms=20, color='lawngreen')      #mark target's position by pixel coordinates
    plt.plot(xpix+220, ypix, 's', marker='_', mew=4, ms=20, color='lawngreen')      #(position, marker, thicknes, length, color)
    plt.savefig(ntd+'/locda.png', dpi=100, bbox_inches='tight', pad_inches=0)      #save plot
    im = PIL.Image.open(ntd+'/locda.png')                                             #reopen image to edit with pil
    im = im.convert("RGB")
    im = im.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    im.save(ntd+'/locda.png', "PNG") 
    im.close()
    
    
    #IMAGE FROM DSS DATABASE
    p=fits.open(fts)                                                              #load fits file
    ra = p[0].header['OBJRA'].replace('h',':').replace('m', ':').replace('s','')    #find ra and dec in header
    dec = p[0].header['OBJDEC'].replace('d',':').replace('m', ':').replace('s','')
    #url to image location, h & w are in arc minutes, Fov=roboaoFov*2.5
    DSSad = "http://archive.stsci.edu/cgi-bin/dss_search?v=poss2ukstu_red&r="+ra+"&d="+dec+"&e=J2000&h=1.4848&w=1.4848&f=gif&c=none&fov=NONE&v3="
    urllib.urlretrieve(DSSad, j+'/locdb.png')                                       #save dss image as png
    im = PIL.Image.open(j+'/locdb.png')                                             #reopen image to edit with pil
    im = im.convert("RGB")
    im = im.transpose(PIL.Image.FLIP_LEFT_RIGHT)                                    #flip image to match roboao data
    draw = ImageDraw.Draw(im)  
    cx = im.size[0]/2                                                               #coordinates of image's center
    cy = im.size[1]/2
    draw.line((cx-10,cy,cx-7,cy),fill=(50, 205, 50))                                #mark image center (target)
    draw.line((cx+10,cy,cx+7,cy),fill=(50, 205, 50))
    draw.rectangle([cx*3/5, cy*3/5, 7*cx/5, 7*cy/5], outline=(52, 40, 44))          #draw square around roboao field (2/5 dimnsns)
    del draw
    im.save(ntd+'/locdb.png', "PNG") 
    im.close()
    
    #FITS COLLAGE (4 pngs)
    fig = plt.figure(k+1, frameon=False)
    fig.set_size_inches(10,10)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.imshow(ftsim, cmap='gray')                              #black and white original fits
    plt.xlim(xpix-sp, xpix+sp)                                 #crop plot based on arcsec specifications
    plt.ylim(ypix-sp, ypix+sp)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fig.savefig(ntd+'/fc1.png', dpi=100, bbox_inches='tight', pad_inches=0)
    
    fig = plt.figure(k+2, frameon=False)
    fig.set_size_inches(10,10)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.imshow(-ftsim, cmap='RdYlBu')                           #color scale original fits
    plt.xlim(xpix-sp, xpix+sp)                                 #crop plot based on arcsec specifications
    plt.ylim(ypix-sp, ypix+sp)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fig.savefig(ntd+'/fc2.png', dpi=100, bbox_inches='tight', pad_inches=0)
    
    fig = plt.figure(k+6, frameon=False)
    fig.set_size_inches(10,10)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.imshow(psf, cmap='gray')                                #black and white psf
    plt.xlim(xpsf-sp, xpsf+sp)
    plt.ylim(ypsf-sp, ypsf+sp)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fig.savefig(ntd+'/fc3.png', dpi=100, bbox_inches='tight', pad_inches=0)
    
    fig = plt.figure(k+7, frameon=False)
    fig.set_size_inches(10,10)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.imshow(psf, cmap='viridis')                                #color psf
    plt.xlim(xpsf-sp, xpsf+sp)
    plt.ylim(ypsf-sp, ypsf+sp)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fig.savefig(ntd+'/fc4.png', dpi=100, bbox_inches='tight', pad_inches=0)
    
    #Larger Field Image (with bright pixels 'cut out')
    ftsimcut = ftsim.copy()
    fig = plt.figure(k+5, frameon=False)
    fig.set_size_inches(10,10)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    fig.add_axes(ax)
    ax.imshow(ftslgn, cmap='gist_ncar')                          #color scaling
    plt.xlim(xpix-232, xpix+232)                            #Crop out to 8 arc seconds (total width of field): 8*1000/(17.4*2)
    plt.ylim(ypix-232, ypix+232)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    fig.savefig(ntd+'/flft.png', dpi=100, bbox_inches='tight', pad_inches=0)
    
    #CREATE COLLAGE
    ftslst=sorted(glob.glob(ntd+'/fc*.png'))                  #open 4 pngs for collage
    images = map(Image.open, ftslst)
    widths, heights = zip(*(i.size for i in images))        #get image dimmensions
    total_width = sum(widths)                               #find total dimmensions of final collage
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))    #create new image
    new_im.paste(images[0], (0,0))                          #add all 4 pngs to new image
    new_im.paste(images[1], ((total_width/4),0))
    new_im.paste(images[2], ((total_width/2),0))
    new_im.paste(images[3], ((total_width*3/4),0))
    new_im.save(ntd+'/ffc.png', "PNG")                        #save new image, the final collage
    new_im.close()
    os.remove(ntd+'/fc1.png')                                 #delete all 4 images used to make collage
    os.remove(ntd+'/fc2.png')
    os.remove(ntd+'/fc3.png')
    os.remove(ntd+'/fc4.png')
    
    m+=1
    k+=10  #keep plots for each target seperate
print 'Done'
