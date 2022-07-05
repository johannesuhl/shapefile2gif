# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:21:53 2022

@author: Johannes H. Uhl, University of Colorado Boulder, USA.
"""

import os,sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg # image module for image reading
import glob
from PIL import Image    
from PIL import ImageDraw
from PIL import ImageFont 
import geopandas as gp
import matplotlib
matplotlib.rcParams['font.sans-serif'] = "Arial"
matplotlib.rcParams['font.family'] = "sans-serif"

### user-specified parameters: ##################################################

in_shp = 'mtbf33_wgs84_08013_boulder_subset.shp' ## shapefile with temporally annotated vector objects
img_dir = './img' ## a subfolder where images will be stored (needs to exist)
year_col = 'year_built' ## year / time stamp column name in shapefile
years=np.arange(1900,2016,1) ## defines for which years we plot
framesecs=[75] ## duration of each frame (year) in output gif in ms. An output will be created for each element of framesecs
figsize = (5,5) ##format of output image
resize=False ##optional downsampling
resize_factor=2 ##downsampling factor

### slice gdf by year attribute and plot #########################################
gdf=gp.read_file(in_shp)
gdf=gdf[gdf[year_col]>0]
bbox = gdf.total_bounds
for year in years:
    yrdf=gdf[gdf[year_col]<=year]
    fig,ax=plt.subplots()  
    ax = yrdf.plot(facecolor="black", edgecolor="none",figsize=figsize)    
    ax.set_title(year)
    ax.set_axis_off() 
    ax.set_xlim([bbox[0],bbox[2]])
    ax.set_ylim([bbox[1],bbox[3]])     
    fig = ax.get_figure()    
    fig.savefig(img_dir+os.sep+'%s.png' %(year),dpi=150)                    
    plt.clf()
    plt.show()    
    print(year)

### read the png image files into frames list####################################
currfiles=[] 
for file in os.listdir(img_dir):
    currfiles.append(img_dir+os.sep+file)
frames = [Image.open(image) for image in currfiles] #.crop((2,2,Image.open(image).size[0]-2,Image.open(image).size[1]-2))
years= [x.split('_')[-1].replace('.png','') for x in currfiles]

### add text to the images  #####################################################
frames_wtext=[]
counter=-1
width=frames[0].width
height=frames[0].height
for f in frames: #[:10]
    counter+=1
    year=years[counter]
    #### add text
    I1 = ImageDraw.Draw(f)         
    myFont = ImageFont.truetype('arial.ttf', 100)         
    I1.text((width/2,618), year, font=myFont,fill =(255,255,255),anchor='mm')  
    myFont = ImageFont.truetype('arial.ttf', 25) 
    I1.text((width/2,35), 'Building evolution in Boulder, Colorado, USA (1900-2015)', font=myFont,fill =(0, 0, 0),anchor='mm')        
    myFont = ImageFont.truetype('arial.ttf', 18) 
    I1.text((width/2,710), 'Data source: MTBF-33 Multi-temporal building footprint dataset', font=myFont,fill =(0, 0, 0),anchor='mm')              
    I1.text((width/2,730), 'Animation created by Johannes H. Uhl, University of Colorado Boulder, 2022.', font=myFont,fill =(0, 0, 0),anchor='mm')              
    frames_wtext.append(f)  
    print(year)    
frames=frames_wtext

### optional resampling to reduce file size######################################
if resize:
    width, height = frames[0].size
    frames = [x.resize((int(width/resize_factor),int(height/resize_factor)),0) for x in frames]

### extend the first and last frame #############################################
duplicate_times=20
start=[]
end=[]
for i in range (duplicate_times):
    start.append(frames[0])
    end.append(frames[-1])
frames=start+frames+end

### export frames to GIF: #######################################################
for framesec in framesecs:
    frame_one = frames[0]
    outfile='mtbf_boulder_%s.gif' %(framesec)
    frame_one.save(outfile, format="GIF", append_images=frames[1:],
               save_all=True, duration=framesec, loop=0)

### clean up: ###################################################################
for file in currfiles:
    os.remove(file)
