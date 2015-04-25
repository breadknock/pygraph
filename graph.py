######################################################
##  'PyChart'                                       ##
##  Graphical representation of data in directories ##
##  Last revision: 21 April 2013                    ##
##  Author: Christopher Brenon                      ##
######################################################

import os
import sys
import math
from Tkinter import *
import tkFont
import tkMessageBox
from os.path import getsize
import random

##CONSTANTS##
kilo = 1024.0       # number of bytes in a kilobyte
pi_size = 500       # diameter of the pie chart, width of the bar chart
bar_size = pi_size  # width of the bar chart
bar_height = 100    # height of the bar chart
x_start = 50        # beginning x,y position of the charts
y_start = 50
text_diff = 40      # distance between text describing each section
max_size = 18
max_num = 10
# list of colors appearing in the chart
# Randomly select from basic color scheme
col = {1:'0',2:'8',3:'f'}
colors = []
for i in xrange(1,4):
    for j in xrange(1,4):
        for k in xrange(1,4):
            colors.append('#'+col[i]+col[i]+col[j]+col[j]+col[k]+col[k])
random.shuffle(colors)

# command line arguments

# -b: whether the chart is a bar chart
b = FALSE
if '-b' in sys.argv:
    b = TRUE
# -h: whether to hide hidden files
h = FALSE
if '-h' in sys.argv:
    h = TRUE
# where to graph from (default is cwd)
pat = '.'
if len(sys.argv) > 1:
    if sys.argv[1][0]!='-':
        pat = sys.argv[1]
# see if this directory is valid
if not os.path.isdir(pat):
    print '\''+str(pat) + '\' is not an existing directory'
    sys.exit(0)

class Section:
    def __init__(self,size,name):
        self.size = size
        self.name = name

def block_size(size):
    return math.ceil(size/4096.0)*4096

#   recursively gets the size of a directory
def dir_size(source):
    total_size = block_size(os.path.getsize(source))
    for item in os.listdir(source):
        itempath = os.path.join(source, item)
        if os.path.islink(itempath):
            continue
        if os.path.isfile(itempath):
            total_size += block_size(os.path.getsize(itempath))
        elif os.path.isdir(itempath):
            total_size += block_size(dir_size(itempath))
    return total_size

def dotdot(string):
    if len(string) > max_size:
        return string[:max_size]+'...'
    return string   

#   returns a file size ('size') in human-readable form
def file_size(size):
    c = 'B'
    if size >= kilo:
        size = size/kilo
        c = 'kB'
        if size >= kilo:
            size = size/kilo
            c = 'MB'
            if size >= kilo:
                size = size/kilo
                c = 'GB'
                #   sort of unnecessary
                if size >= kilo:
                    size = size/kilo
                    c = 'TB'
                    #   getting out of hand...
                    if size >= kilo:
                        size = size/kilo
                        c = 'PB'
                        #   ...just stop.
                        if size >= kilo:
                            size = size/kilo
                            c = 'EB'
                            #   You'd better end here...
                            if size >= kilo:
                                size = size/kilo
                                c = 'ZB'
                                #   Ha, at least you have nothing left now!
                                if size >= kilo:
                                    size = size/kilo
                                    c = 'YB'
                                    #   When would this ever happen...?
                                    if size >=kilo:
                                        print 'How\'s the future?'
    return (str(size)[:5]+" "+c)

#   changes 'sections' to be a list of the files in directory 'path'
#       returns the total size
def getSections(path,sections):
    total = 0
    try:
        for line in os.listdir(path):
            if (h or line[0]!='.'):
                if os.path.islink(path+'/'+line):
                    continue
                elif os.path.isdir(path+'/'+line):
                    size = dir_size(path+'/'+line)
                else:
                    size = block_size(os.path.getsize(path+'/'+line))
                sections.append(Section(size,line))
                total+=size
        return total
    except Exception:
        print 'Permission denied to \''+str(os.path.abspath(path))+'\''
        sys.exit(0)

#   draws a pie chart or bar graph detailing the usage by sections
def draw(path,removed,sections,total):
    itr = iter(colors)  # iterates through chart colors
    secs = []           # lists the pie sections of the graph
    ids = dict()        # corresponds the pie sections to their Section
    root = Tk()
    root.title("Files in: "+os.path.abspath(path))
    C = Canvas(root, height=800, width=1000)
    far = 0
    if b:
        far = x_start
    move = 1
    if total != 0:
        for sec in sections:
            if (sec.size*1.0/total)>(1.0/bar_size) and (not sec.name in removed):
                try:
                    color = itr.next()
                except StopIteration:
                    itr = iter(colors)
                    color = itr.next()
                if b:
                    a = C.create_rectangle(far,y_start,far+sec.size*bar_size/total,y_start+bar_height,fill = color)
                    secs.append(a)
                    ids[a] = sec
                    far+=sec.size*bar_size/total
                else: 
                    if(sec.size==total):
                        a = C.create_oval(x_start,y_start,x_start+pi_size,y_start+pi_size,fill = color)
                        secs.append(a)
                        ids[a] = sec
                        far = 360;
                    else:
                        a = C.create_arc(x_start,y_start,x_start+pi_size,y_start+pi_size,start = far,extent=sec.size*360.0/total,fill = color)
                        secs.append(a)
                        ids[a] = sec
                        far+=sec.size*360.0/total
                C.create_text(650,text_diff*move,text=dotdot(sec.name),anchor=W)
                C.create_rectangle(610,text_diff*(move)-text_diff/4,610+text_diff/2,text_diff*move+text_diff/4,fill=color)
                C.create_text(800,text_diff*move,text=file_size(sec.size),anchor=W)
                move+=1
        if not b:
            if far < 360-1.0/bar_size:
                try:
                    color = itr.next()
                except StopIteration:
                    itr = iter(colors)
                    color = itr.next()
                C.create_arc(x_start,y_start,x_start+pi_size,y_start+pi_size,start = far,extent = 360-far,fill = color)
                C.create_text(610+text_diff,text_diff*move,text="Other",anchor=W)
                C.create_rectangle(610,text_diff*move-text_diff/4,610+text_diff/2,text_diff*move+text_diff/4,fill=color)
                move+=1
        if not b:
            C.create_text(x_start+pi_size/2.0,y_start+pi_size+20,text="Total: "+file_size(total),anchor=N,font=("Helvetica","16"))
    if(len(removed)>0):
        C.create_text(610+text_diff,text_diff*(move+1),text="Removed:",anchor=W)
        move+=1
    for line in removed:
        C.create_text(610+text_diff,text_diff*(move+1),text=line,anchor=W)
        move+=1
    #   called on left-click: opens another window with an image of the directory that was clicked on in the chart
    def clicker(event):
        if not b:
            if math.sqrt((event.y-(y_start+pi_size/2.0))**2+(event.x-(x_start+pi_size/2.0))**2) < (pi_size/2.0):
                far = 0
                for sec in sections:
                    if(sec.size*1.0/total>1.0/bar_size) and not sec.name in removed:
                        far+=sec.size*360.0/total
                        if far > (-math.degrees(math.atan2(event.y-(y_start+pi_size/2.0),event.x-(x_start+pi_size/2.0)))+360)%360:
                            if os.path.isdir(path+'/'+ sec.name):
                                root.destroy()
                                new_sections = []
                                new_total = getSections(path+'/'+sec.name,new_sections)
                                draw(path+'/'+ sec.name,[],new_sections,new_total)
                                draw(path,removed,sections,total)
                            break
        else:
            if (event.y<y_start+bar_height and event.y > y_start and event.x > x_start and event.x < x_start+bar_size):
                far = x_start
                for sec in sections:
                    if(sec.size*1.0/total>1.0/bar_size) and not sec.name in removed:
                        far+=sec.size*bar_size/total
                        if far > event.x:
                            if os.path.isdir(path+'/'+ sec.name):
                                root.destroy()
                                new_sections = []
                                new_total = getSections(path+'/'+sec.name,new_sections)
                                draw(path+'/'+ sec.name,[],new_sections,new_total)
                                draw(path,removed,sections,total)
                            break
    root.bind("<Button-1>",clicker)

    #   called on right click: removes the clicked file/directory from the pie chart
    def remover(event):
        if not b:
            if math.sqrt((event.y-(y_start+pi_size/2.0))**2+(event.x-(x_start+pi_size/2.0))**2) < (pi_size/2.0):
                far = 0
                for sec in sections:
                    if(sec.size*1.0/total>1.0/bar_size) and not sec.name in removed:
                        far+=sec.size*360.0/total
                        if far > (-math.degrees(math.atan2(event.y-(y_start+pi_size/2.0),event.x-(x_start+pi_size/2.0)))+360)%360:
                            removed.append(sec.name)
                            root.destroy()
                            draw(path,removed,sections,total-sec.size)
                            break
        else:
            if (event.y<y_start+bar_height and event.y > y_start and event.x > x_start and event.x < x_start+bar_size):
                far = x_start
                for sec in sections:
                    if(sec.size*1.0/total>1.0/bar_size) and not sec.name in removed:
                        far+=sec.size*bar_size/total
                        if far > event.x:
                            removed.append(sec.name)
                            root.destroy()
                            draw(path,removed,sections,total-sec.size)
                            break
    root.bind("<Button-3>",remover)

    # Hover text
    text = C.create_text(x_start+pi_size/2.0,700,anchor=N,font=("Helvetica","16"))
    text2 = C.create_text(x_start+pi_size/2.0,740,anchor=N,font=("Helvetica","16"))
    def printer(event,tag):
        C.itemconfigure(text,text=ids[tag].name)
        C.itemconfigure(text2,text = file_size(ids[tag].size))
    for secx in secs:
        lam = lambda event,tag=secx: printer(event,tag)
        C.tag_bind(secx,"<Enter>",lam)
    C.pack()
    root.mainloop()
    
#   draw the graph for the directory specified in command line (default cwd)
sections = []
total = getSections(pat,sections)
draw(pat,[],sections,total)
