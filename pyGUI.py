#ideas:
# Use http get/post requests as opposed to reading from text file
# make two different "nodes"
# make a place for sending commands
# have a button to refresh serial ports available
# IMPROVE EFFICIENCY - works but not well
# Scale for mobile or make two different javascript files

# Define Libraries
from tkinter import *
import serial.tools.list_ports
import time
import csv
import datetime
import os
from ftplib import FTP

p = 0
data = []
htmlData = []
comPort = ""; #declare comPort so it can be global
ftpSuccess = True
ser = serial.Serial() # Global serial port. Declared later on after port is selected

# header list will vary based on payload
header = "Payload  \t Min \t Sec \t Lat \t Long \t Alt(m) \t AG(m) \t eT(F) \t iT(F) \t P1(PSI) \t P2(PSI) \t R? \t millis() \t\t additional messages" # GUI header
headerList = header.split("\t") # break up the created header so it can be used to make the web app header
severalSpaces = "&nbsp&nbsp&nbsp&nbsp&nbsp" # several spaces to act as a tab in html
htmlHeader = severalSpaces.join(headerList) # create the header that will be used in the web app

def initFTP(): # Needs to be able to skip over if there is no connection
    global ftp
    global ftpSuccess

    try:
        ftp = FTP('andrewvangerpen.com') # location of the server
        ftp.login(user='bnajqrmy', passwd = 'MNSGCBallooning1!') # server login info
        ftp.cwd('/public_html/Ballooning') # path on the directory
    except:
        ftpSuccess = False

def initFiles():
    global webFileName
    global fileName
    webFileName = "Ballooning.txt" # We want to make this obsolete!!!! This is the file that will be written to in the remote directory on the web server
    if os.path.exists(webFileName): # If the file already exists in the path, remove it
        os.remove(webFileName)
    today = datetime.datetime.now() # retrieve the current date and time from the local machine
    fileDay = "DataDate" + today.strftime("%m-%d-%y") # create a file folder labeled with the date
    if os.path.exists(fileDay) == False: # if the folder does not exist with this name, make directory
        os.makedirs(fileDay)
    fileTime = "DataTime" + today.strftime("%H-%M-%S") + ".csv" # create the file name in the "day folder" that is labeled with the exact time
    fileName =  os.path.join(fileDay, fileTime) # merge folder and file

def initTK():
    global root
    global ports
    global frame_main
    global label_canvas
    global frame_canvas
    global frame_data
    global canvas
    global vsb
    global writer
    global file
    global filename


    root = Tk() # label tkinter as root
    root.title("Test GUI") # Title on window
    root.grid_rowconfigure(0, weight=1) # weight here causes the row to take up more space than necessary
    root.columnconfigure(0, weight=1) # ""

    ports = serial.tools.list_ports.comports() # gather all serial ports

    frame_main = Frame(root,bg="maroon") # create a frame in root
    frame_main.grid(sticky='news', columnspan = 10) # idk

    label_canvas = Label(frame_main, text = header, height = 2, font=('Helvetica', '12'), bg="gold") # create a permanent header at the top of the GUI
    label_canvas.grid(row=0, column=1,sticky='nw') # place the label
    frame_canvas = Frame(frame_main) # create a new frame in the main frame
    frame_canvas.grid(row=1, column=1, rowspan = 10, sticky='nw') # place the canvas
    frame_canvas.grid_rowconfigure(0, weight=1) # again, weight causes the row to take up more space than necessary
    frame_canvas.grid_columnconfigure(0, weight=1)
    frame_canvas.grid_propagate(False) # cannot resize

    canvas = Canvas(frame_canvas, bg="white")
    canvas.grid(row=0, column=0, sticky="news")
    vsb = Scrollbar(frame_canvas, orient="vertical", command = canvas.yview) # create a scroll bar in the text canvas
    vsb.grid(row=0,column=1,sticky='ns') # Place the verical scroll bar
    canvas.configure(yscrollcommand=vsb.set) # set the vertical scroll bar

    frame_data = Frame(canvas,bg="white")
    canvas.create_window((10,0), window=frame_data, anchor = 'nw')
    columns_width = 1200
    rows_height = 800

    frame_canvas.config(width=columns_width + vsb.winfo_width(), height= rows_height)
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1)

    frame_command = Frame(frame_main, bg = "maroon").grid(row=50, column = 1, columnspan = 10, sticky = 'ne')

    payloadIDLabel = Label(frame_command, text = "Payload ID:" ,font=('Helvetica', '28')).grid(row=10, column=1, sticky="sw")
    payloadID = Entry(frame_command,font=('Helvetica', '28')).grid(row=10, column=4, sticky="sw")
    commandLabel = Label(frame_command, text = "Command:" , font=('Helvetica', '28')).grid(row=10, column=5, sticky="sw")
    commandText = Entry(frame_command,font=('Helvetica', '28')).grid(row=10, column=6, columnspan = 10, sticky="sw")

def choosePort():
    global frame_main
    global ports
    i=0
    while (i < len(ports)): # this is janky but I think it is the only real way to make buttons for each available COM port, add a way to refresh this list
        global k
        k = len(ports)
        if(i==0):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'), command = lambda: mySerial(0)).grid(row=0, column=0, sticky="W")
        if(i==1):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(1)).grid(row=1, column=0, sticky ="W")
        if(i==2):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(2)).grid(row=2, column=0, sticky ="W")
        if(i==3):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'),command = lambda:mySerial(3)).grid(row=3, column=0, sticky ="W")
        if(i==4):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'),command = lambda:mySerial(4)).grid(row=4, column=0, sticky ="W")
        if(i==5):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(5)).grid(row=5, column=0, sticky ="W")
        if(i==6):
            Button(frame_main, text=ports[i], height = 2, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(6)).grid(row=6, column=0, sticky ="W")
        i=i+1
initFTP()
initFiles()
initTK()
choosePort()

def writeWebFile():
    global webFileName
    global htmlData
    global htmlHeader

    webFile = open(webFileName, 'w+') # open the local file that we are going to upload to the remote directory
    webFile.write(htmlHeader + "<br>") # write to the web file the header with an html endline
    for y in range(len(htmlData)): # write the last x-number of data strings to the web app
        webFile.write(str(htmlData[y]) + "<br>")
    webFile.close() # close the file after adding the data. One problem seems to be that the jquery in the web app is pulling .txt data while the file is being written
def placeFile():
    global p
    global webFileName
    ftp.storbinary('STOR '+ webFileName, open(webFileName, 'rb')) # send the file via the ftp client

def mySerial(number):
    currentPort = str(ports[number])
    global ser
    global k
    global comPort

    comPort = str(currentPort.split(' ')[0]) # Shortens the COM port + description (bluetooth, UART, etc.) to just the COM port

    print("com port: " + comPort) # Write current COM port below available ports
    k = len(ports)
    Label(frame_main, text=comPort, height = 2, width = 40, font=('Helvetica', '12'), bg='maroon').grid(row=k, column=0) # Write down the current COM port

    ser.baudrate = 9600
    ser.port = comPort # Declare the serial we are using with the correct COM port
    ser.open() # open the serial port to receive data

    time.sleep(1) # delay for a second so we can clear the port
    k = k + 1 # increment the row number - might not need this

    openFile()
    retrieveData() # run more startup code

def openFile():
    global file
    global writer

    file = open(fileName,'w') # Open CSV file to write to
    writer = csv.writer(file, lineterminator='\n') # Write to the csv file
    ser.flushInput() # flush the input so there's no partial data strings

def retrieveData():
    global p
    global data
    global htmlData
    global setUpBool
    global htmlFileString
    global canvas
    global vsb
    global writer

    if(ser.in_waiting > 10):

        frame_data.update_idletasks()
        recentData = ser.readline() # read last data line from the
        fileString = str(recentData).partition("!")[0] # eliminate exclamation mark and other characters associated with bowers xbee protocol
        fileList = fileString.split(",") # split up the data string into a string list
        tabs = "\t"
        htmlTabs = "&nbsp&nbsp&nbsp&nbsp&nbsp" # fake html tab. A bunch of spaces
        fileString = tabs.join(fileList) # make a new string seperated by tabs for GUI display
        htmlFileString = htmlTabs.join(fileList) # make a new string seperated by "tabs" for web app
        writer.writerow(fileList)
        data.append(fileString)
        htmlData.append(htmlFileString)
        if(len(htmlData)>30):
            del htmlData[0]

        Label(frame_data, text = data[p], font=('Helvetica', '11'),bg="white").grid(row=p,column=1) # write every single data string
        p = p+1

        writeWebFile()
        if(ftpSuccess == True):
            placeFile()

    root.after(100,retrieveData) # rerun function after this many ms

root.mainloop()
