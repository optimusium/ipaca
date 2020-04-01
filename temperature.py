import os
import re
import time

#initialize alert file
inf0=open("alert_initial.csv","r")
inf0.readline()
outf0=open("alert.csv","w+")
outf0.write("Name,Alert,Temperature\n")
for line in inf0.readlines():
    outf0.write(line)
outf0.close()
inf0.close()
time.sleep(0.01)

os.popen("copy alert.csv alert_bk.csv")
time.sleep(0.1)

while 1:
    #getting blacklist
    blacklist=[]
    inf9=open("blacklist.csv","r")
    inf9.readline()
    for line in inf9.readlines():
        line=line.replace("\n","")
        if line=="": continue
        buf=re.split(",",line)
        if buf[0]!="":
            blacklist.append(buf[0])
        
    #print("Who are you? Please give me your name")
    #name=input()
    ##print("Please key in your temperature")
    #temp=eval(input())
    #tim=time.time()
    #image login is from image recognition
    try:
        inf=open("image_login.csv","r")
    except:
        time.sleep(1)
        inf=open("image_login.csv","r")
        pass
    #generating alert file
    try:
        outf=open("alert.csv","w+")
    except:
        time.sleep(1)
        outf=open("alert.csv","w+")
        pass
    outf.write("Name,Alert,Temperature\n")
    bufl=""
    latest=99999.0
    inf.readline()
    for line in inf.readlines():
        line=line.replace("\n","")
        buf=re.split(",",line)
        if len(buf)<2: continue
        #print(eval(buf[1]),latest)
        if eval(buf[1])>latest:
            latest=eval(buf[1])
            bufl=buf[0]
    ter=""
    ter+=bufl+","
    if bufl in blacklist:
        temp = 99
        print("Please Stay Where You Are - Someone Will Come Over.")
        ter+="2,%s\n" % temp
        outf.write(ter)
        
    print("Please key in your temperature")
    temp=eval(input()) 
    print("temp = ", temp)
    tim=time.time()
    
    if bufl in blacklist:
        temp = 99        
    elif temp>=38:
        ter+="1,%s\n" % temp
    else:
        ter+="99999,%s\n" % temp
    outf.write(ter)
    for line in inf.readlines():
        line=line.replace("\n","")
        buf=re.split(",",line)
        if buf[1] in blacklist:
            ter+=buf[1]+"2,%s\n" % temp
        elif buf[1]!=bufl:
            ter=buf[1]+",99999,%s\n" % temp
    outf.write(ter)
    outf.close()
    inf.close()
    time.sleep(0.01)

    os.popen("copy alert.csv alert_bk.csv")
    time.sleep(0.1)
    

