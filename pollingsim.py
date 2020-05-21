from tkinter import Frame
import tkinter
import threading
import time
from PIL import Image, ImageTk
from collections import deque
import random

control=[0,0,0]     # program running, sleep on/off, gui running
stations=[]          # lista threads stathmon
            #0     1       2       3       4       5
colors=['black','red','#ec00ed','green','#e9e9e9','blue']   # lista xromaton gia grigori xrisi
CHANCE=5            # % pithanotita paragogis paketou gia tous stathmous
LIMIT=8           # elaxistos arithmos paketwn pou tha metadothoun ana kombo
STARTING_RANGE=2    # euros arxikou arithmou paketwn stis oures kathe station, 0 - STARTING RANGE

class channel():
   def __init__(self):     # klasi antikeimenou channel pou periexei
      self.msg='-1'        # to minima pou metadidetai sto kanali
      self.state=0         #tin katastasi tou kanaliou
      self.ttotal=0        # sinolikos xronos pou exei perasei

class packet():
   def __init__(self,birth):
      self.birth=birth     # xroniki stigmi gennisis paketou dedomenwn

class station (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID         #arithmos kathe stathmou 0-9
      self.name = name
      self.x=0
      self.y=0                         # sintetagmenes sto GUI
      self.p2t=deque([])               # oura paketwn
      self.sent=0                      # arithmos paketwn pou exei steilei
      self.tput=0                      # timi throughput
      self.max_delay=0
      self.mean_delay=0
      self.total_delay=0
      j=random.randint(0,STARTING_RANGE)  # tixaia arxikopoihsi twn ourwn apo 0 ws 2 paketa 
      for i in range(j):
         self.p2t.append(packet(channel.ttotal))
      self.tr_status=[4,4,4]         #rack, sack, sdata. tra smission status tou stathmou ( dinontas katallili timi analoga me to 
      self.ch_x=0                     # ti dedomena dexetai i stalnei o stathmos, elegxw to xrwma tou kanaliou tou kathe stathmou)
   def run(self):
      global control                            
      def tdelay(c,pack,stat):         # sinartisi pou metraei to delay otan stelnetai ena data paketo
         pdelay=c.ttotal-pack          # delay = sinolikos xronos pou exei parelthei - to pote genithike to sigekrimeno paketo
         stat.sent+=1
         primary_.sent+=1
         if pdelay>stat.max_delay:     # vriskw an einai max
            stat.max_delay=pdelay
         stat.total_delay+=pdelay
         stat.mean_delay=stat.total_delay/stat.sent   # kai epanupologizw to meso delay
      #print ("Starting " + self.name)
      while control[0]==0:                            # MAIN LOOP kathe stathmou
         if (random.randint(0,101)<=CHANCE)and(len(self.p2t)<5):  # tixaios arithmos apo 0-100 ki an mikroteros tis pithanotitas pou thelw kai an den einai gemati i oura
            self.p2t.append(packet(channel.ttotal))               # gennisi paketou
         if control[1]==0:
            time.sleep(1)                                         # kathisterisi tou thread gia 1 deuterolepto
         if (channel.msg=="p"+str(self.threadID))and(len(self.p2t)>0):   # an to minima sto kanali apeuthinetai sto stathmo kai iparxoun paketa pros metadosi
            if control[1]==0:
               time.sleep(1)
            if self.threadID%2==0:                                # elegxw an o stathmos einai aristera i dexia tou kanaliou gia na kanw katallilo pop() (aristera oi artioi, dexia oi perittoi)
               sentpacket=self.p2t.pop()       
            else:
               sentpacket=self.p2t.popleft()
            tdelay(channel,sentpacket.birth,self)                 # ipologismos delay meta tin afairesi tou stoixeiou apo tin oura
            self.tr_status=[4,4,3]                                # allazw to transmission status gia na ftiaxw to xrwma
            channel.msg="data"                                    # to minima sto kanali einai twra data
            channel.ttotal+=10                                    # o xronos sto kanali auxanetai kata ton xrono tou data paketou
            channel.state=3
         elif (channel.msg=="p"+str(self.threadID))and(len(self.p2t)==0):     #an den iparxoun paketa pros metadosi
            channel.msg="nack"                                    # stelnetai paketo negative acknowledgment
            channel.ttotal+=1                                     # auxisi tou xronou tou kanaliou kata xrono tou poll paketou
            self.tr_status=[4,2,4]
            channel.state=2                                       # orismos metavlitwn pou boithan sto xrwmatismo sto GUI
         if control[1]==0:
            time.sleep(1)
         self.tr_status=[4,4,4]
         self.tput=self.sent/channel.ttotal                       # ipologismos throughput sto telos kathe loop
      #while control[2]==0:
      #   pass
      #print ("Exiting " + self.name)
      return

class primary (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.x=330
      self.y=55
      self.tput=0
      self.max_delay=0
      self.mean_delay=0
      self.sent=0
   def run(self):
      global control
      def poll(i):                           # sinartisi po kanei poll ton i stathmo
         channel.msg="p"+str(i)              # to minima sto kanali ginetai 'p(arithmos stathmou)' px. p1 p2 p3
         channel.ttotal+=1                   # auxisi xronou sto kanali kata xrono tou poll paketou
         stations[i].tr_status=[1,4,4]
         channel.state=1
      #print ("Starting " + self.name)
      while control[0]==0:                   # MAIN LOOP kentrikou stathmou
         i=0
         while (i<10) and (control[0]==0):                              # gia kathe stathmo
            poll(i)                                                     # poll
            while (channel.msg[0]=="p") and (control[0]==0):            # oso to minima einai akoma poll (den exei lifthei apo kapoio stathmo)
               pass                                                     # perimene
            i+=1
            self.tput=0
            self.max_delay=0                                            #sinolika dedomena throughput max delay kai meso delay
            self.mean_delay=0
            finflag=0                                                   # flag gia n katalavw an oloi oi stathmoi esteilan ton elaxisto arithmo paketwn
            for j in range(10):                                         # gia kathe stathmo
               self.tput+=stations[j].tput
               if stations[j].max_delay>self.max_delay:                 # upologismos tous
                  self.max_delay=stations[j].max_delay
               self.mean_delay+=stations[j].mean_delay/10
               if stations[j].sent<LIMIT:                               # elegxos arithmou paketo pou exoun stalthei
                  finflag=1
            if finflag==0:
               control[0]=1
            if control[1]==0:                                           # kathisterisi 1 sec
               time.sleep(1)
            self.tput=self.sent/channel.ttotal                          
      #while control[2]==0:
      #   pass
      #print ("Exiting " + self.name)
      return

class gui (threading.Thread, Frame):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name=name
   def run(self):
      global control
      global colors
      global stations
      packets = [[0 for a in range(5)] for b in range(10)]
      ms = [[0 for a in range(4)] for b in range(10)]
      oms = []
      finals = []
      racks=[]
      sacks=[]                            # metavlites pou periexoun ta diafora antikeimena pou sxediazontai
      sdata=[]
      finalms=[]
      even_x=170
      odd_x=330
      st_y=120
      cables=[]
      def exit():                         # sinartisi pou trexei otan patithei to koupi close
         canvas.delete(tkinter.ALL)       # diagrafei oti exei sxediastei
         window.destroy()                 # kleinei to parathiro
         control[0]=1                     # stamataei to loop twn stathmwn
         control[2]=1                     # kai tou GUI
      def finish():
         control[1]=1                     #sinartisi pou parakamptei ta sleeps sta threads kai odigei se grigoroteri ektelesi
      #print ("Starting " + self.name)

      window = tkinter.Tk()
      window.title("Polling Protocol Simulation")        # parametroi ekkinisis tou parathurou
      window.geometry("1000x800+300+50")
      canvas = tkinter.Canvas(window, width = 1000, height = 800)  #creating the 'Canvas' area
      
      def drawPrimaryStation(x,y):
         hh=80/2
         hw=55/2
         left=x-hw               # sxediasmos ikonidiou kentrikou stathmou me xrisi diaforwn sximatwn
         right=x+hw
         top=y-hh
         bot=y+hh
         canvas.create_rectangle(left, top, right, bot, fill = "grey") #frame
         canvas.create_rectangle(left+4, top+4, left+hw-2, top+4+20, fill = "blue") #core1
         canvas.create_rectangle(left+4, top+26, left+hw-2, top+26+20, fill = "blue") #core2
         canvas.create_rectangle(right-hw+2, top+4, right-4, top+4+20, fill = "blue") #core3
         canvas.create_rectangle(right-hw+2, top+26, right-4, top+26+20, fill = "blue") #core4
         canvas.create_oval(left+4, y+11, left+11, y+18, fill="red") #led1
         canvas.create_oval(left+17, y+11, left+24, y+18, fill="red") #led2
         canvas.create_oval(left+30, y+11, left+37, y+18, fill="red") #led3
         canvas.create_oval(left+43, y+11, left+50, y+18, fill="red") #led4
         canvas.create_line(left+4,bot-14,right-4,bot-14,width=3,fill="yellow") #line1
         canvas.create_line(left+4,bot-7,right-4,bot-7,width=3,fill="green") #line2
         canvas.create_text(x,y+50,fill="darkblue",font="Arial 8 bold", #text
                        text="Primary Station")
      def drawStation(x,y,i):
         hh=55/2
         hw=40/2
         left=x-hw            # to idio gia tous ipoloipous stathmous
         right=x+hw
         top=y-hh
         bot=y+hh
         canvas.create_rectangle(left, top, right, bot, fill = "grey") #frame
         canvas.create_line(left,y+10,right,y+10,width=2,fill="black") #blackline
         canvas.create_rectangle(x+14, y+13, x+18, y+17, fill = "green") #pb
         canvas.create_line(x+4,y-19,right,y-19,width=2,fill="yellow") #line1
         canvas.create_line(x+4,y-10,right,y-10,width=2,fill="yellow") #line2
         canvas.create_line(x+4,y-2,right,y-2,width=2,fill="yellow") #line3
         canvas.create_text(x,y+36,fill="darkblue",font="Arial 8 bold", #text
                        text="Station "+str(i))
         drawQueue(x,y, i,stations[i].p2t)
      def drawQueue(x,y,i,j):
         canvas.create_rectangle(x-50, y+45, x+50, y+65, fill = "white") #frame
         if (i%2)==0:                                       # sxediasmos tis ouras kathe stathmou analoga an gemizei
            pointer=x+40                                    # apo ta aristera i apo ta dexia
            orient='right'
            q_offset=-60
         else:
            pointer=x-40
            orient='left'
            q_offset=60
         drawTriangle(x+q_offset,y+55,'black',orient)
         for j in range (5):
            packets[i][j]=canvas.create_rectangle(pointer-8, y+47, pointer+8, y+63,outline='white', fill = "black") #packet
            if (i%2)==0:
               pointer-=20
            else:
               pointer+=20
      def drawTriangle(x,y,color,orient):
         if orient=='up':
            points=[x,y-10,x-10,y+5,x+10,y+5]
         elif orient=='left':
            points=[x-10,y,x+5,y-10,x+5,y+10]
         elif orient=='right':
            points=[x+10,y,x-5,y-10,x-5,y+10]
         elif orient=='down':
            points=[x,y+10,x-10,y-5,x+10,y-5]

         canvas.create_polygon(points, outline='black', fill=color, width=2)
      def drawRecAck(x,y,i):
         if i%2==0:
            racks.append(canvas.create_text(x+42,y+8,fill="red",font="Arial 8 bold", text="<-POLL")) #sxediazontai oi endeixeis
         else:
            racks.append(canvas.create_text(x-42,y+8,fill="red",font="Arial 8 bold", #text
                        text="POLL->"))
      def drawSendAck(x,y,i):
         if i%2==0:
            sacks.append(canvas.create_text(x+48,y+17,fill="red",font="Arial 8 bold", #text
                        text="NACK->"))
         else:
            sacks.append(canvas.create_text(x-48,y+17,fill="red",font="Arial 8 bold", #text
                        text="<-NACK"))
      def drawSendData(x,y,i):
         if i%2==0:
            sdata.append(canvas.create_text(x+48,y-10,fill="green",font="Arial 8 bold", #text
                        text="DATA->"))
         else:
            sdata.append(canvas.create_text(x-48,y-10,fill="green",font="Arial 8 bold", #text
                        text="<-DATA"))
      def drawRTMetrics(x,y,j):
         canvas.create_text(x,y,fill="darkblue",font="Arial 12 bold", text=j.name)
         ms[j.threadID][0]=canvas.create_text(x+10,y+20,fill="darkblue",font="Arial 10 bold", text="Throughput: "+str(j.tput/10))
         ms[j.threadID][1]=canvas.create_text(x+10,y+40,fill="darkblue",font="Arial 10 bold", text="Max Delay: "+str(j.max_delay/10))     #sxediasmos ton metrisewn
         ms[j.threadID][2]=canvas.create_text(x+10,y+60,fill="darkblue",font="Arial 10 bold", text="Mean Delay: "+str(j.mean_delay/10))
         ms[j.threadID][3]=canvas.create_text(x+10,y+80,fill="darkblue",font="Arial 10 bold", text="Packets sent: "+str(j.sent))
      def drawOMetrics(x,y,j):
         canvas.create_text(x,y,fill="#d6018d",font="Arial 12 bold", text="Overall")
         oms.append(canvas.create_text(x+10,y+20,fill="#d6018d",font="Arial 10 bold", text="Throughput: "+str(j.tput/10)))
         oms.append(canvas.create_text(x+10,y+40,fill="#d6018d",font="Arial 10 bold", text="Max Delay: "+str(j.max_delay/10)))
         oms.append(canvas.create_text(x+10,y+60,fill="#d6018d",font="Arial 10 bold", text="Mean Delay: "+str(j.mean_delay/10)))
         oms.append(canvas.create_text(x+10,y+80,fill="#d6018d",font="Arial 10 bold", text="Packets sent: "+str(j.sent)))
      def drawFinals(x,y):
         canvas.create_text(x,y,fill="red",font="Arial 12 bold", text="Final")
         finalms.append(canvas.create_text(x+10,y+20,fill="red",font="Arial 10 bold", text="Max Delay: "))
         finalms.append(canvas.create_text(x+10,y+40,fill="red",font="Arial 10 bold", text="Mean Delay: "))
      tkinter.Button(window, text = "Close", command=exit).place(x=765, y=750) #exit button
      dchannel = canvas.create_line(250,40,250,750,width=10,fill="black")       # kentriko kanali
      tkinter.Button(window, text = "Skip", command=finish).place(x=695, y=750) # koumpi to opoio parakamptei tin kathisterisi tou kathe thread
      canvas.pack()

      my=10
      mx=600
      for i in range (10):
         if (i%2)==1:
            st_y-=75
            stations[i].x=odd_x
            stations[i].ch_x=odd_x-20
         else:                                                                   # sxediasmos antikeimenwn pou aforoun ton kathe stathmo
            stations[i].x=even_x
            stations[i].ch_x=even_x+20
         stations[i].y=st_y
         drawStation(stations[i].x, stations[i].y, stations[i].threadID)
         cables.append(canvas.create_line(stations[i].ch_x,stations[i].y,250,stations[i].y,width=5,fill="black"))
         drawRecAck(stations[i].x,stations[i].y,stations[i].threadID)
         drawSendAck(stations[i].x,stations[i].y,stations[i].threadID)
         drawSendData(stations[i].x,stations[i].y,stations[i].threadID)
         st_y+=105
         drawRTMetrics(mx,my,stations[i])
         my+=120
         if i==4:
            mx=850
            my=10

      canvas.create_line(500,595,1000,595,width=3,fill="black")
      drawOMetrics(850,610,primary_)
      #drawFinals(850,610)
      drawPrimaryStation(primary_.x,primary_.y)
      pr_cable=canvas.create_line(primary_.x-55/2,primary_.y,250,primary_.y,width=5,fill="black")   # kalwdia pou sundeoun tous stathmous sto kanali
      canvas.create_text(600,610,fill="black",font="Arial 12 bold", text="Current Message")
      polled=canvas.create_text(600,630,fill="black",font="Arial 12 bold", text=channel.msg)         # current timi paketou
      canvas.create_text(600,670,fill="black",font="Arial 12 bold", text="Time elapsed in data packets")
      disptotal=canvas.create_text(600,690,fill="black",font="Arial 12 bold", text=channel.ttotal/10)    # sinolikos xronos

      while control[2]==0:
         canvas.itemconfig(dchannel, fill=colors[channel.state])                                    #--------MAIN LOOP GUI--------
         for i in range (10):
            canvas.itemconfig(cables[i], fill="black")
            for l in range (3):
               if stations[i].tr_status[l]!=4:
                  canvas.itemconfig(cables[i], fill=colors[stations[i].tr_status[l]])                 # se auto to loop oles ta parapanw antikeimena pou sxediastikan
            canvas.itemconfig(racks[i], fill=colors[stations[i].tr_status[0]])                        # ananewnontai sinexws kai xanasxediazontai
            canvas.itemconfig(sacks[i], fill=colors[stations[i].tr_status[1]])                        # me vasi tis nees times apo tin ektelesi twn threads
            canvas.itemconfig(sdata[i], fill=colors[stations[i].tr_status[2]])
            for j in range (len(stations[i].p2t)):
               canvas.itemconfig(packets[i][j], fill="black")
            for k in range (len(stations[i].p2t),5):
               canvas.itemconfig(packets[i][k], fill="white")
            
            canvas.itemconfig(ms[i][0], text="Throughput: "+str(round(stations[i].tput/10,4)))
            canvas.itemconfig(ms[i][1], text="Max Delay: "+str(stations[i].max_delay/10))
            canvas.itemconfig(ms[i][2], text="Mean Delay: "+str(round(stations[i].mean_delay/10,2)))
            canvas.itemconfig(ms[i][3], text="Packets sent: "+str(stations[i].sent))
         if channel.msg[0]=="p":
            canvas.itemconfig(pr_cable, fill="red")
         elif channel.msg=="nack":
            canvas.itemconfig(pr_cable, fill=colors[2])
         else:
            canvas.itemconfig(pr_cable, fill="black")
         canvas.itemconfig(polled, text=channel.msg)
         canvas.itemconfig(disptotal, text=channel.ttotal/10)
         canvas.itemconfig(oms[0], text="Throughput: "+str(round(primary_.tput/10,4)))
         canvas.itemconfig(oms[1], text="Max Delay: "+str(primary_.max_delay/10))
         canvas.itemconfig(oms[2], text="Mean Delay: "+str(round(primary_.mean_delay/10,2)))
         canvas.itemconfig(oms[3], text="Packets sent: "+str(primary_.sent))
         window.update()                                                                              # ananewsi parathirou
        
      #print ("Exiting " + self.name)    
      return 

channel=channel()                                           # dimiourgia instance gia to kanali

# Create threads
for i in range (10):
   stations.append(station(i, "Thread-Station "+str(i)))    # dimiourgia twn threads twn stathmwn kai tou GUI
primary_=primary(11, "Overall")
gui_ = gui(12, "Thread-GUI")

# Start Threads
for i in range (10):
   stations[i].start()                                      # ekkinisi twn proigoumenwn threads
primary_.start()
gui_.start()

#wait = input("PRESS ENTER TO CONTINUE.")

stations[0].join()
stations[1].join()
stations[2].join()
stations[3].join()
stations[4].join()                                          # ta threads kleinoun edw otan teleiwsoun to loop tous
stations[5].join()
stations[6].join()
stations[7].join()
stations[8].join()
stations[9].join()

print ("Final Max Delay: "+str(primary_.max_delay/10))
print ("Final Mean Delay: "+str(round(primary_.mean_delay/10,2)))       # ektipwsi twn telikwn timwn stin konsola