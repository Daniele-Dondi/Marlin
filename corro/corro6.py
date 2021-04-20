 # Program CORRO
 #
 # Copyright (c) 2021 Daniele Dondi
 #
 # This program is free software: you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program.  If not, see <https://www.gnu.org/licenses/>.
 #
 #
import PIL.Image
from threading import Timer
import tkinter
import threading
import math
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import dialog
from tkinter import ttk
import time
import datetime
import os
#import serial
from os import listdir
from os.path import isfile, join
import sys
sys.path.append('/home/pi/Printrun') #put here your path to Printrun software
#from printrun.printcore import *
#from printrun.utils import *
#from printrun import gcoder
import logging

#global vars
connected = 0
robot = 0      #printrun handle for robot
syringe = 0    #printrun handle for syringe
electrodes = 0 #serial handle
T_Actual = 0
T_SetPoint = 0
Temp_points=[]
MAX_Temp=10
V1_points=[]
MAX_V1=0.0
V2_points=[]
MAX_V2=0.0
last_V1=0.0
last_V2=0.0
macrolist = [] #list of avail macros
macrob=[]      #macro button array
IsEditingMacro=0
IsDeletingMacro=0
visible = 1
chart_w=800 #size of the temp and voltages chart
chart_h=600
w_fullsize=True #chart starts fullsize. It can be resized with F1
macrout=0      #global var for macros. Filled when macro returns a value
pixboundedmacro=[] # list of macros bound to pixels
colorsbound=[]     # list of colors bound. Refers to above macros name
NewColorAssignment=0 # if a user assign a color during runtime this var is set to 1
logfile=0
Gcode0=[]
IsBuffered0=False
#following parameters must be read from configuration.txt file
NumSyringes=0 #Number of installed syringes
SyringeMax=[1,2,3,4,5,6] #Syringe max millimeters
SyringeVol=[1,2,3,4,5,6] #Syringe max volume
VolInlet=0
VolOutlet=0
SchematicImage="" #file name for the image
MaskImage=""      #file name for the mask image
MaskMacros=""     #file name for the bounded colors to macros


def showscheme():
    global visible
    global chart_h,chart_w,w_fullsize
    if w_fullsize:
     chart_w=200
     chart_h=200
     w.config(width=chart_w,height=chart_h)
     IM.pack() #show graphic control
     w_fullsize=False
    else: 
     chart_w=800
     chart_h=600
     w.config(width=chart_w,height=chart_h)
     IM.pack_forget() #hide graphic control
     w_fullsize=True

def resize():
    global visible
    global chart_h,chart_w,w_fullsize
    if visible==1:
     Z.pack_forget()   
     F.pack_forget()
     visible = 0
    else:
     Graph.pack_forget() #hide chart
     IM.pack_forget() #hide graphic control
     F.pack(side="left",fill="y")
     Z.pack(side="left",fill="y")
     Graph.pack(side="left")
     if not(w_fullsize): IM.pack() #show graphic control
     visible = 1
    

def keypress(event):  #keyboard shortcuts
    if event.keysym == 'Escape': #quit program
        Close()
    if event.keysym == 'Alt_L': #show/hide commands
        resize()
    if event.keysym == 'F1': #resize chart canvas
        showscheme()

def readConfigurationFiles():
    global NumSyringes,SyringeMax,SyringeVol,VolInlet,VolOutlet,SchematicImage,MaskImage,MaskMacros,colorsbound,pixboundedmacro
    try:
        conf_file = open("configuration.txt", "r")
        lines=conf_file.readlines()
        conf_file.close()
        NumSyringes=int(lines[1].strip())
        for x in range(NumSyringes):
            l=lines[3+x].split(";")
            SyringeMax[x]=float(l[0].strip())*2 #annoyngly we have to multiply by 2 to have the correct movement in mm
            SyringeVol[x]=float(l[1].strip())
        curline=4+NumSyringes
        VolInlet=float(lines[curline].strip())
        curline+=2
        VolOutlet=float(lines[curline].strip())
        curline+=2
        SchematicImage=lines[curline].strip()
        MaskImage=SchematicImage.rsplit( ".", 1 )[ 0 ]+"-mask.png"
        MaskMacros=SchematicImage.rsplit( ".", 1 )[ 0 ]+"-binds.txt"
    except:    
     tkinter.messagebox.showerror("ERROR","Error reading configuration file. Please quit program")

    try:
     bind_file = open(MaskMacros, "r")
     lines=bind_file.readlines()
     bind_file.close()
     NumBinds=int(lines[1].strip())
     for x in range(NumBinds):        
      pixboundedmacro.append(lines[3+x].strip())
      colorsbound.append(eval(lines[4+x+NumBinds]))
    except:
     tkinter.messagebox.showwarning("Warning","Current schematic has no colors defined with macros")


def onclick(event):
    global pix
    global pixboundedmacro, colorsbound    
    print ("clicked at", event.x, event.y)
    color=pix[event.x,event.y]
    print (color)
    if color in colorsbound:
     macroname=pixboundedmacro[colorsbound.index(color)]   
     print(macroname)
     try:
       macronum=macrolist.index(macroname)
       Macro(macronum,str(color[0])+','+str(color[1])+','+str(color[2])) #by default passes color arguments to macro
     except:
       tkinter.messagebox.showerror("ERROR","Problem executing macro "+macroname)  

def onmiddleclick(event):
    global pix
    global pixboundedmacro, colorsbound    
    print ("clicked at", event.x, event.y)
    color=pix[event.x,event.y]
    print ('middle',color)
    if color in colorsbound:
     MsgBox = tkinter.messagebox.askquestion ('Unbound color','Are you sure you want to unbound macro for this color?',icon = 'warning')
     if MsgBox == 'yes':
      idx=colorsbound.index(color)
      del colorsbound[idx]
      del pixboundedmacro[idx]

def onrightclick(event):
    global pix
    print ("right clicked at", event.x, event.y)
    color=pix[event.x,event.y]
    print (color)
    binder = tkinter.Toplevel(base)
    binder.title("bind an event to this color")
    Label(binder,text='bind an event to this color').pack()
    comboMacro = ttk.Combobox(binder, values=macrolist, width=40)
    comboMacro.pack()
    Button(binder, text="OK",command=lambda: Bind(comboMacro.get(),color,binder)).pack()
    Button(binder, text="CANCEL",command=lambda: binder.destroy()).pack()
    binder.grab_set()

def Bind(text,color,window):
    global pixboundedmacro, colorsbound,NewColorAssignment
    if text=="" or text==None: return
    if text in macrolist:
      if not(color in colorsbound):
          colorsbound.append(color)
          pixboundedmacro.append(text)
          window.destroy()
          print('macro ',text,' assigned to color ',color)
          NewColorAssignment=1
      else:     tkinter.messagebox.askquestion ('error','color already assigned',icon = 'warning')
    else:     tkinter.messagebox.askquestion ('error','macro not found',icon = 'warning')  
  
         
#Main window
base = Tk()
#base.attributes("-fullscreen", True) #go FULLSCREEN
base.bind('<Key>', keypress)
F = Frame(base)
F.pack(side="left",fill="y")
Z = Frame(base,bd=2,relief=RIDGE) #macros frame
Z.pack(side="left",fill="y")
K = Frame(F)
K.pack(side="bottom")
J = Frame(F)
J.pack(side="bottom")
I = Frame(F)
I.pack(side="bottom")
H = Frame(F)
H.pack(side="bottom")
G = Frame(F)
G.pack(side="bottom")
Graph=Frame(base)
Graph.pack(side="left")
w=Canvas(Graph,width=chart_w,height=chart_h)
w.pack(expand=YES,fill=BOTH)

w.create_text(chart_w/2,50,font=("Verdana",20),text="COntrollo Remoto Robotico",fill="black")
dt=w.create_text(chart_w/2,200,font=("Verdana",14),text="DISCONNECTED",fill="white")
rt=w.create_rectangle(w.bbox(dt),fill="black")
w.tag_lower(rt,dt)

IM=Frame(base)
IM.pack(side="left")
w2=Canvas(IM,width=600,height=400)
w2.bind("<Button-1>", onclick) #bind click procedure to graphic control
w2.bind("<Button-2>", onmiddleclick) #bind click procedure to graphic control
w2.bind("<Button-3>", onrightclick) #bind click procedure to graphic control
w2.pack()
#insert here the load config file  TODO
readConfigurationFiles()
Aimage=PhotoImage(file=SchematicImage) # load the scheme of the current configuration
w2.create_image(0, 0, image = Aimage, anchor=NW)
im = PIL.Image.open(MaskImage) # load the mask here
'''
print (im.size) #get image size
print (NumSyringes)
print (SyringeMax)
print (SyringeVol)
print (VolInlet)
print (VolOutlet)
print(SchematicImage)
print(MaskImage)
'''
pix = im.load()
IM.pack_forget()
showscheme()

#FUNCTIONS

def SaveMacro(text,macronumber,window): #save a macro
    if macronumber==-1:
        while True:
         filename = tkinter.simpledialog.askstring('MACRO NAME','Please assign a name to this macro')
         if filename in macrolist: tkinter.messagebox.showerror("ERROR","Macro name already in use. Choose another name")
         elif filename == "": tkinter.messagebox.showerror("ERROR","Please assign a name")
         elif filename == None:
             tkinter.messagebox.showerror("ERROR","Macro will not be saved")
             window.destroy()
             return
         else: break
        macronumber=len(macrolist)
        macrolist.append(filename)
        macrob.append(Button(Z, text=filename,command=lambda j=macronumber : Macro(j)))
        macrob[len(macrob)-1].pack()
    text_file = open("macros/"+macrolist[macronumber]+".txt", "w")
    text_file.write(text)
    text_file.close()
    window.destroy()

def MacroEditor(macronumber): #edit a macro or create a new one
     if macronumber!=-1: title=macrolist[macronumber] #-1 : new macro
     else: title='NEW MACRO'
     t = tkinter.Toplevel(base)
     t.title(title)
     a=Text(t,width=50,height=30)
     if macronumber!=-1:
        text_file = open("macros/"+macrolist[macronumber]+".txt", "r")
        text=text_file.read()
        text_file.close()
        a.insert(INSERT, text)
     a.pack()
     Button(t, text="SAVE",command=lambda: SaveMacro(a.get("1.0",END),macronumber,t)).pack()
     Button(t, text="CANCEL",command=lambda: t.destroy()).pack()
     t.grab_set()
     
def SubstituteVarValues(line,variables): #substitute values to var names $var$ in a string
    global macrout
    for var in range(0,len(variables),2):
        line=line.replace(variables[var],str(variables[var+1]))
    line=line.replace('$return$',str(macrout))
    return line    

def RefreshVarValues(var_name,value,variables): #if a variable exists, update its value. If it does not exist, create it
    if not(var_name in variables):
       variables.append(var_name)#save var name
       variables.append(value)          #save value
    else:
      variables[variables.index(var_name)+1]=value

def Parse(line,variables):    #parse macro lines and executes statements
    global logfile,IsBuffered0,Gcode0
    global SyringeMax, SyringeVol, VolInlet, VolOutlet #global parameters for syringes taken from configuration.txt
    line = line.split(";", 1)[0] #remove comments (present eventually after ;)
    line=line.rstrip()  #remove cr/lf
    if line=="": return
    if line.find('log')==0: #print string to log file
     try:
      commands=line.split(' ',1)
      #commands[0]=commands[0][4:] # remove log
      print(commands[1])
      commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
      logfile.write(commands[1]+"\n")
     except:
      tkinter.messagebox.showerror("ERROR in log method","use: log text")
    elif line.find('buffer')==0: #buffer all commands, send later. Used for long gcode sequence where send will fail
        IsBuffered0=True
        Gcode0=[]
    elif line.find('print')==0: #send all buffered commands. Used for long gcode sequences
        if (IsBuffered0):
            IsBuffered0=False
            StartPrint0()
    elif line.find('ask')==0: #if ask, make question to user
     try:
      commands=line.split(',',6)
      commands[0]=commands[0][4:] # remove ask
      x = tkinter.simpledialog.askinteger(commands[1], commands[2]+' ['+str(commands[4])+'..'+str(commands[5]+']'),initialvalue=int(commands[3]), minvalue=int(commands[4]), maxvalue=int(commands[5]))
      if x==None: x=0
      RefreshVarValues(commands[0],x,variables)
     except:
      tkinter.messagebox.showerror("ERROR in ask method","use: ask $varname$,title,question,initialvalue,minvalue,maxvalue")
    elif line.find('getsyringeparms')==0: #load the values for the syringe  
     try:
      axisnames=["X","Y","Z","I","J","K"]   
      commands=line.split(' ',1)
      commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
      RefreshVarValues("$syringemax$",SyringeMax[int(commands[1])],variables)
      RefreshVarValues("$syringevol$",SyringeVol[int(commands[1])],variables)
      RefreshVarValues("$volinlet$",VolInlet,variables)
      RefreshVarValues("$voloutlet$",VolOutlet,variables)
      RefreshVarValues("$axisname$",axisnames[int(commands[1])],variables)
     except:
      tkinter.messagebox.showerror("ERROR in getsyringeparms method","use: getsyringeparms syringenumber")
    elif line.find('eval')==0: #we've to calculate somethg
      try:
       commands=line.split(',',1)
       commands[0]=commands[0][5:] # remove eval
       x = eval(SubstituteVarValues(commands[1],variables)) #substitute variable names with values
       RefreshVarValues(commands[0],x,variables)
      except:
       tkinter.messagebox.showerror("ERROR in eval method","use: eval $varname$,math_expression")
    elif line.find('exec')==0: #we've to execute somethg
      try:
       commands=line.split('!,')
       commands[0]=commands[0][5:] # remove exec
       code=SubstituteVarValues(commands[0],variables) #substitute variable names with values
       code=code.replace('/n',os.linesep) # /n in code is translated in newline
       commands=commands[1].split(',')
       codevars=[]
       namevars=[]
       for x in range(0,len(commands)):
        temp=commands[x].split('=')   
        codevars.append(temp[0])
        namevars.append(temp[1])
       g=dict()
       l=dict()
       exec(code,g,l)
       for x in range(0,len(namevars)):
           RefreshVarValues(namevars[x],l[codevars[x]],variables)
      except:
       tkinter.messagebox.showerror("ERROR in exec method","use: exec code!,varname1=$var1$,...")       
    elif line.find('macro')==0: #we've to call a nested macro
      try:
       commands=line.split('"',2)
       try:
        num=macrolist.index(commands[1])
        if commands[2]!="": Macro(num,SubstituteVarValues(commands[2],variables))
        else:
         Macro(num)
       except ValueError:  tkinter.messagebox.showerror("ERROR in macro call",'macro '+commands[1]+' does not exist')
      except:
       tkinter.messagebox.showerror("ERROR in macro call",'use: macro "macroname" var1,var2..')
    elif line.find('echo')==0: #we've to echo to the console
      try:
       commands=line.split(' ',1)
       commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
       print(commands[1])
      except:
       tkinter.messagebox.showerror("ERROR in echo method","use: echo text $varname$")
    elif line.find('message')==0: #create a messagebox
      try:
       commands=line.split(' ',1)
       commands[1]=SubstituteVarValues(commands[1],variables) #substitute var names with values
       tkinter.messagebox.showinfo('info',commands[1])
      except:
       tkinter.messagebox.showerror("ERROR in message method","use: message text $varname$")
    elif line.find('send')==0:
      try:
       commands=line   
       commands=line.split(',',1)
       commands[0]=commands[0][5:] # remove send
       commands[0] = SubstituteVarValues(commands[0],variables) #substitute variable names with values
       sendcommand(commands[0],int(commands[1]))
      except IOError:
       tkinter.messagebox.showerror("ERROR in send method","use: send command,where")
    else:
        #command not recognized
        print('unknown command',SubstituteVarValues(line,variables))

def Macro(num,*args): #run a macro. Call Parse function for line by line execution. Delete a macro or edit
    global IsEditingMacro,IsDeletingMacro,macrob,macrout
    watchdog=0
    variables=[]
    stack=[] #stack keeps line numbers for cycles
    labels=[] #labels are special variables containing line numbers to be used for goto and jump instructions
    for ar in args:
      #print('params',ar)
      par=ar.split(',')
      for x in range(0,len(par)):
          RefreshVarValues('$'+str(x+1)+'$',par[x],variables)
    if IsEditingMacro==0:
     if IsDeletingMacro==0:
      if connected==0:   
        MsgBox = tkinter.messagebox.askquestion ('Not Connected','Connect?',icon = 'warning')
        if MsgBox == 'yes':  Connect()
      if connected==1:   
       print('executing macro:',macrolist[num])
       with open('macros/'+macrolist[num]+'.txt') as macro_file:
        lines=macro_file.readlines() #read the entire file and put lines into an array
        i=0
        for j in range(len(lines)):
         line=lines[j]   
         if (line.find('label')==0): #before executing the code search all the labels and put them into the label array
           label=line.split(' ',1)
           RefreshVarValues(label[1],i,labels)  # insert the current line number in the labels set
        while (i<len(lines)):
         line=lines[i]
         i=i+1
         watchdog=watchdog+1
         if (watchdog>500): #try to avoid infinite loops
          MsgBox = tkinter.messagebox.askquestion ('Infinite Loop?','It seems that we are doing a lot of cycles. Continue?',icon = 'warning')
          if MsgBox == 'yes':
           watchdog=0
          else: return 
         isfor=line.find('for')==0
         isnext=line.find('next')==0
         islabel=line.find('label')==0
         isjump=line.find('jump')==0
         isif=line.find('if')==0
         if (isfor|isnext|islabel|isjump|isif): #in the case of for/next, label, jump and if statements, the code is analyzed in this section and not in the command parser
          if isfor: #for
           stack.append(i)
           var=line.split(' ',2)
           stack.append(var[1].rstrip())
           value=int(SubstituteVarValues(var[2].rstrip(),variables))
           RefreshVarValues(var[1],value,variables)
           print(stack)
          elif isnext: #next
           for_variable=stack[-1]
           value=int(SubstituteVarValues(for_variable,variables))-1
           RefreshVarValues(for_variable,value,variables)
           if value>0:
            i=int(stack[-2])
            line=lines[i]
           else: 
            del(stack[-1])
            del(stack[-1])
          elif isjump: #jump (unconditioned jump)
           label=line.split(' ',1)
           try:
            i=int(SubstituteVarValues(label[1],labels))
           except:
            tkinter.messagebox.showerror("ERROR in jump","label not defined")
          elif isif: #if statement
           label=line.split(' ',2)
           if (SubstituteVarValues(label[1],variables))=="True":
            try:
             i=int(SubstituteVarValues(label[2],labels))
            except:
             tkinter.messagebox.showerror("ERROR in if","label not defined")
         else:    
          Parse(line,variables) #execute code contained in line
       if '$return$' in variables: macrout=SubstituteVarValues("$return$",variables)
       print (variables)  #DEBUG
      else:  tkinter.messagebox.showerror("ERROR","Not connected. Connect first")
     else:  #delete macro
      MsgBox = tkinter.messagebox.askquestion ('Delete macro','Are you sure you want to delete macro '+macrolist[num]+" ?",icon = 'warning')
      if MsgBox == 'yes':
        macrob[num].destroy()
        os.remove("macros/"+macrolist[num]+".txt")
        macrolist[num]=""  
      DeleteMacro()  
    else: #edit macro
     MacroEditor(num)   
     EditMacro()


def CreateMacro():
     global IsEditingMacro,IsDeletingMacro
     if IsDeletingMacro==1: DeleteMacro()
     if IsEditingMacro==1: EditMacro()
     MacroEditor(-1) #-1 = create new macro
     
def EditMacro():
    global IsEditingMacro,IsDeletingMacro
    if IsEditingMacro==0:
     ToggleB.config(relief=SUNKEN)
     IsEditingMacro=1
     if IsDeletingMacro==1: DeleteMacro()
     base.config(cursor='cross')
    else:
     IsEditingMacro=0
     ToggleB.config(relief=RAISED)
     base.config(cursor='arrow')          

def DeleteMacro():
    global IsEditingMacro,IsDeletingMacro
    if IsDeletingMacro==0:
     ToggleB2.config(relief=SUNKEN)
     IsDeletingMacro=1
     if IsEditingMacro==1: EditMacro()
     base.config(cursor='pirate')
    else:
     IsDeletingMacro=0
     ToggleB2.config(relief=RAISED)
     base.config(cursor='arrow')     

#Quit program
def Close():
 global pixboundedmacro, colorsbound,NewColorAssignment,MaskMacros
 if connected != 0:
     tkinter.messagebox.showerror("ERROR","Disconnect first")
 else:    
  MsgBox = tkinter.messagebox.askquestion ('Exit Application','Are you sure you want to exit the application?',icon = 'warning')
  if MsgBox == 'yes':  
     #insert here the save config file  TODO
     if NewColorAssignment==1:
        MsgBox = tkinter.messagebox.askquestion ('Save color assignment','Do you want to save new assignments?',icon = 'question')
        if MsgBox == 'yes':
         out_file = open(MaskMacros, "w")
         out_file.write("#num of bound colors\n")
         out_file.write(str(len(pixboundedmacro))+"\n#pixboundedmacro\n")
         for pix in pixboundedmacro:
          out_file.write(pix+"\n")
         out_file.write("#colorbound\n")
         for col in colorsbound:
          out_file.write(str(col)+"\n")          
         out_file.close()
         print(pixboundedmacro)
         print(colorsbound)
     base.destroy()

def ResetChart():
  global Temp_points
  global MAX_Temp
  global V1_points, V2_points
  global MAX_V1,MAX_V2
  Temp_points=[]
  MAX_Temp=10
  V1_points=[]
  MAX_V1=0.0
  V2_points=[]
  MAX_V2=0.0
 
    

#Robot direct interface for buttons
def MoveRobot(cmd):
 global connected
 if connected==1:
  how_much=step.get()
  if cmd=='XY0': robot.send("G28 X Y")
  elif cmd=='Z0': robot.send("G28 Z")
  elif cmd=='+Y':
    robot.send("G91") #relative positioning
    robot.send("G1 Y"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='+X':
    robot.send("G91") #relative positioning
    robot.send("G1 X"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='+Z':
    robot.send("G91") #relative positioning
    robot.send("G1 Z"+str(how_much))
    robot.send("G90") #absolute positioning    
  elif cmd=='-Y':
    robot.send("G91") #relative positioning
    robot.send("G1 Y-"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='-X':
    robot.send("G91") #relative positioning
    robot.send("G1 X-"+str(how_much))
    robot.send("G90") #absolute positioning
  elif cmd=='-Z':
    robot.send("G91") #relative positioning
    robot.send("G1 Z-"+str(how_much))
    robot.send("G90") #absolute positioning    
 else:    tkinter.messagebox.showerror("ERROR","Not connected. Connect first")
  

def sendcommand(cmd,where): #send a gcode command
    global connected,IsBuffered0
    destination=['Syringe','Robot']
    if connected==1:
      '''  
      if where==0:  #0 = syringe
       if (IsBuffered0):
           Gcode0.append(cmd)
       else:
        syringe.send(cmd)
      else:         #1 = robot
       robot.send(cmd)
      ''' 
      print(cmd,"->",destination[where])
    else:    tkinter.messagebox.showerror("ERROR","Not connected. Connect first")

def StartPrint0(): #print gcode
    global connected,syringe,Gcode0
    Gcode0 = gcoder.LightGCode(Gcode0)    
    syringe.startprint(Gcode0)
    

def Draw_Chart(data,maximum,xtextpos,color):  #update graph
        w.create_text(xtextpos,10,text="{:.2f}".format(maximum),fill=color)        
        num_points=len(data)        
        pp=[]
        if num_points>2:
         w.create_text(chart_w-xtextpos-10,10,text="{:.2f}".format(data[-1]),fill=color)   
         if num_points<chart_w:
             endloop=num_points
         else:
             endloop=chart_w
         for x in range(0,endloop):
          index=round((x+1)*num_points/endloop)
          pp.append(x)
          pp.append(round(chart_h-data[index-1]*chart_h/maximum))
         w.create_line(pp,fill=color)


def filter_import_messages(record): #update temperature values. Filter out all other messages from Marlin
    global T_Actual, T_SetPoint, logfile
    if (record.msg.find(' B:')>0 and record.msg.find('root')<0):
        temp=record.msg[record.msg.find('B')+2:record.msg.find('@')]; #filter all messages but temperature
        #print(temp)
        [T_Actual, T_SetPoint]=temp.split('/',2)
    return False

        

logger = logging.getLogger().addFilter(filter_import_messages)     # bind filtering to printer messages

def Connect(): #connect to robot, syringe and electrodes. Start cycling by calling MainCycle
    global connected, robot, syringe, electrodes, logfile
    if connected == 0 :
        connected = 1
        '''
        try:
         robot=printcore('/dev/ttyUSB0',250000)
        except:
         tkinter.messagebox.showerror("ERROR", "ROBOT not connected! \ncheck connections\nand restart")
        try:
         syringe=printcore('/dev/ttyUSB1',250000)
         syringe.loud=True         
        except:
         tkinter.messagebox.showerror("ERROR", "SYRINGE unit not connected! \ncheck connections\nand restart")
        setup_logging(sys.stdout,None,False)
        time.sleep(2)        
        try:
         electrodes = serial.Serial('/dev/ttyACM0', 9600)
        except:
         tkinter.messagebox.showerror("ERROR", "Electrodes not connected! \ncheck connections\nand restart")
        try:
            logfile=open("log.txt","a")
            logfile.write("----------------------------------\n")
            logfile.write("-         PROCESS STARTS         -\n")
            logfile.write("----------------------------------\n")
            logfile.write(str(datetime.datetime.now())+"\n")
        except:
           tkinter.messagebox.showerror("ERROR", "Error writing log file")
        threading.Timer(0.1, MainCycle).start()
        '''        
    else:
     MsgBox = tkinter.messagebox.askquestion ('Disconnect','Are you sure you want to disconnect?',icon = 'warning')
     if MsgBox == 'yes':
      connected=0;
      robot.disconnect()
      syringe.disconnect()
      electrodes.close()
      logfile.write("---------------------------------\n")
      logfile.write("-         PROCESS ENDED         -\n")
      logfile.write("---------------------------------\n")
      logfile.write(str(datetime.datetime.now())+"\n")
      logfile.close()
    



#MAIN CYCLE
def MainCycle():  #loop for sending temperature messages, reading electrodes values and updating graphs
  #global electrodes
  global connected
  global T_Actual, T_SetPoint
  global MAX_Temp
  global V1_points, V2_points
  global MAX_V1,MAX_V2
  global last_V1, last_V2  
  if connected == 1:
   syringe.send_now("M105")
   if electrodes.in_waiting:
        data=electrodes.readline()
        stringa=data.decode("utf-8")
        V=stringa.split('\t')
        if len(V)==3:
            try:
             V1=float(V[1])
             V2=float(V[2])
             last_V1=V1             
             last_V2=V2
             if V1>MAX_V1: MAX_V1=V1+0.1
             if V2>MAX_V2: MAX_V2=V2+0.1             
            except:
             pass
   V1_points.append(last_V1)
   V2_points.append(last_V2)
   Temp_points.append(float(T_Actual))   
   logfile.write(str(T_Actual)+" "+str(T_SetPoint)+" "+str(last_V1)+" "+str(last_V2)+"\n")
   Y1=float(T_Actual)
   Y2=float(T_SetPoint)
   if max(Y1,Y2)>MAX_Temp: MAX_Temp=max(Y1,Y2)+5
   w.delete("all") #clear canvas
   Draw_Chart(Temp_points,MAX_Temp,20,'black')
   if Y2!=0 :          #if temperature setpoint is enabled, draw a dashed line at the value
     setpointp=round(chart_h-Y2*chart_h/MAX_Temp)
     w.create_line(0,setpointp,chart_w,setpointp,dash=(4, 2))
   Draw_Chart(V1_points,MAX_V1,60,'blue')
   Draw_Chart(V2_points,MAX_V2,100,'green')  
   threading.Timer(0.5, MainCycle).start() #call itself

    

#Software name
F.master.title("CO.R.RO")

#Frame F
lTitle = Label(F, text="CO.R.RO",  font=("Verdana 15 bold"))
lTitle.pack(side="top")
bStart = Button(F, text="CONNECT/DISCONNECT", command=Connect)
bStart.pack(side="top", pady=10)
bSend_0 = Button(F, text="Send to syringebot", command=lambda: sendcommand(eCommand_0.get(),0))
bSend_0.pack(pady=10)
lCommand_0 = Label(F, text="Command:")
lCommand_0.pack()
eCommand_0 = Entry(F)
eCommand_0.insert(0, 'M301 P100 I1.5 D800')
eCommand_0.pack()
bSetTemp = Button(F, text="SetTemp", command=lambda: sendcommand("M140 S"+eTemperature.get(),0))
bSetTemp.pack(pady=10)
lTemperature = Label(F, text="Temperature: (°C)")
lTemperature.pack()
eTemperature = Entry(F)
eTemperature.insert(0, 60)
eTemperature.pack()
bSend_1 = Button(F, text="Send to robot", command=lambda: sendcommand(eCommand_1.get(),1))
bSend_1.pack(pady=10)
lCommand_1 = Label(F, text="Command:")
lCommand_1.pack()
eCommand_1 = Entry(F)
eCommand_1.insert(0, 'G28 X Y')
eCommand_1.pack()
Button(F, text="reset chart", command=ResetChart).pack();
bClose = Button(F, text="EXIT", command=Close)
bClose.pack(pady=10)


#Frames G,H,I,J,K
step=StringVar()
lControl = Label(G, text="ROBOT MANUAL CONTROL",font="Verdana 10 bold",bg='pink')
lControl.pack()
Button(H, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(H, text="+Y", command=lambda: MoveRobot('+Y'),width=3).pack(side=LEFT)
Button(H, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(H, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(H, text="+Z", command=lambda: MoveRobot('+Z'),width=3).pack(side=LEFT)

Button(I, text="-X", command=lambda: MoveRobot('-X'),width=3).pack(side=LEFT)
Button(I, text="XY0", command=lambda: MoveRobot('XY0'),width=3).pack(side=LEFT)
Button(I, text="+X", command=lambda: MoveRobot('+X'),width=3).pack(side=LEFT)
Button(I, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(I, text="Z0",command=lambda: MoveRobot('Z0'),width=3).pack(side=LEFT)

Button(J, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(J, text="-Y", command=lambda: MoveRobot('-Y'),width=3).pack(side=LEFT)
Button(J, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(J, text="", state=DISABLED,bd=0,width=3).pack(side=LEFT)
Button(J, text="-Z", command=lambda: MoveRobot('-Z'),width=3).pack(side=LEFT)

Label(K, text="Step:").pack(side=LEFT)
eStep = Entry(K,width=4,textvariable=step)
eStep.pack(side=LEFT)
step.set(10)
Label(K, text="mm/deg").pack(side=LEFT)


#CREATE MACRO BUTTONS in frame Z
try:
 for file in os.listdir("macros"):
    if file.endswith(".txt"):
        macrolist.append(file[:-4]) #remove .txt
except:
    tkinter.messagebox.showerror("ERROR", "MACRO directory unreachable")
else:
  Label(Z, text="MACROS",font="Verdana 10 bold",bg='pink').pack(pady=10)
  Button(Z, text="CREATE MACRO",command=CreateMacro).pack()
  ToggleB=Button(Z, text="EDIT MACRO",command=EditMacro)
  ToggleB.pack()
  ToggleB2=Button(Z, text="DELETE MACRO",command=DeleteMacro)
  ToggleB2.pack()
  Button(Z, text="", state=DISABLED,bd=0).pack() #space between buttons
  i=0
  for macro in macrolist:
   macrob.append(Button(Z, text=macro,command=lambda j=i : Macro(j)))
   macrob[i].pack()
   i=i+1



#Start the main loop
base.mainloop()
