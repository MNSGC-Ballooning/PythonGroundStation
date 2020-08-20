#from ctypes import windll # Library that looks for device display scaling settings so the GUI is not blurry
from tkinter import * # Graphical Library
import serial.tools.list_ports # Accesses devices COM ports
import time # Library that allows time delays within the code
import csv # Library to read/write CSV files
import datetime # Library pulls the time from your device
import os
from PIL import ImageTk,Image # Allows the uploading of images to tkinter (google map)
import requests
import mysql.connector
from mysql.connector import errorcode
import json

try:
    import httplib
except:
    import http.client as httplib

#windll.shcore.SetProcessDpiAwareness(1)

internetConnection = False
uniquePayloads = [] # empty list of unique payload identifiers
payloadFileName = [] # empty list of unique payload file names (tags identifier to the back end)
payloadFile = [] # empty list of unique payload files
dataLabels = []
p = 0 # This will increment all packets recorded while the app is running
data = [] # all data from the payload
comPort = ""; #declare comPort so it can be global
ser = serial.Serial() # Global serial port. Declared later on after port is selected
APRS_APIkey = ""
Google_APIkey = ""

apiKeyFile = open('apiKeys.txt','r') # opens the external file with API keys for google maps and APRS data scraping
for x in apiKeyFile:
    if 'APRS_APIkey:' in x:
        APRS_APIkey = (x[x.find(':') + 1 :]).strip()
    if 'Google_APIkey:' in x:
        Google_APIkey = (x[x.find(':') + 1 :]).strip()

APRSlatitude = ""
APRSlongitude = ""
APRSpath = "&path=color:0xff0000ff|weight:5" # beginning of the APRS path URL extension for the static map
GPSpath = "&path=color:0x0000ff|weight:5" # beginning of the onboard GPS path URL extension for the static map

mapWidth = 800 # static google map width on the GUI
mapHeight = 500 # static google map height on the GUI
mapZoom = 10 # default static map zoom

# header list will vary based on payload
header = "Payload \t Date \t Time \t Lat \t Long \t Alt(ft) \t Sensor1 \t Sensor2 \t Sensor3 \t Sensor4 \t Sensor5 \t millis() \t additional messages" # GUI header
headerList = header.split("\t") # break up the created header so it can be used to make a set of GUI labels

root = Tk() # label tkinter as root
root.title("Test GUI") # Title on window
root.grid_rowconfigure(0, weight=1) # weight here causes the row to take up more space than necessary
root.columnconfigure(0, weight=1) # ""

ports = serial.tools.list_ports.comports() # gather all serial ports
portsLength = len(ports)

def initFiles():
    global fileName
    global today
    global fileDay
    today = datetime.datetime.now() # retrieve the current date and time from the local machine
    fileDay = "DataDate" + today.strftime("%m-%d-%y") # create a file folder labeled with the date
    if os.path.exists(fileDay) == False: # if the folder does not exist with this name, make directory
        os.makedirs(fileDay)
    fileTime = "DataTime" + today.strftime("%H-%M-%S") + ".csv" # create the file name in the "day folder" that is labeled with the exact time
    fileName =  os.path.join(fileDay, fileTime) # merge folder and file

def superposeAPRS():
    global APRSmarker
    global APRSpath
    try:
        callsign = "kd0awk-" + str(callsignNumber.get())
        APRSurl = "https://api.aprs.fi/api/get?name=" + callsign + "&what=loc&apikey=" + APRS_APIkey + "&format=json"
        print(APRSurl)
        r = requests.get(APRSurl)
        cont = r.json()

        APRSlatitude = str(cont['entries'][0]['lat'])
        APRSlongitude = str(cont['entries'][0]['lng'])
        APRSaltitude = str(int(float(cont['entries'][0]['altitude'])/0.3048))
        unixTime = int(cont['entries'][0]['time'])
        APRStime = "Last Packet: " + str(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(unixTime)))

        APRSmarker = "&markers=color:red%7Clabel:A%7C" + APRSlatitude + "," + APRSlongitude
        APRSpath = APRSpath + "|" + APRSlatitude + "," + APRSlongitude

    except:
        APRStime = "Last Query Failed..."

    APRSdata = Label(frame_APRS, text = APRStime, font=('Helvetica', '12'), bg='maroon', fg='gold')
    APRSdata.grid(row = 2, column = 0, columnspan=3, sticky='nw')

    APRSpositionLabel = Label(frame_APRS, text = "Position: " + APRSlatitude +", " + APRSlongitude + " Altitude (ft): " + APRSaltitude , font=('Helvetica', '12'), bg='maroon', fg='gold')
    APRSpositionLabel.grid(row=3, column=0, sticky='nw')

    root.after(60000,superposeAPRS)

def checkInternet(url="www.google.com", timeout=3):
    global internetConnection
    internetConn = httplib.HTTPConnection(url, timeout=timeout)
    try:
        internetConn.request("HEAD", "/")
        internetConn.close()
        internetConnection = True
    except Exception as e:
        internetConnection = False

def myMap():
    updateMaps()

def zoomIn():
    global mapZoom
    mapZoom = mapZoom + 2
    myMap()

def zoomOut():
    global mapZoom
    mapZoom = mapZoom - 2
    myMap()

def choosePort():
    i=0
    while (i < len(ports)): # this is janky but I think it is the only real way to make buttons for each available COM port, add a way to refresh this list
        global k
        k = len(ports)
        if(i==0):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'), command = lambda: mySerial(0)).grid(row=0, column=0, padx=4, sticky="W")
        if(i==1):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(1)).grid(row=1, column=0, padx=4, sticky ="W")
        if(i==2):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(2)).grid(row=2, column=0, padx=4, sticky ="W")
        if(i==3):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'),command = lambda:mySerial(3)).grid(row=3, column=0, padx=4, sticky ="W")
        if(i==4):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'),command = lambda:mySerial(4)).grid(row=4, column=0, padx=4, sticky ="W")
        if(i==5):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(5)).grid(row=5, column=0, padx=4, sticky ="W")
        if(i==6):
            Button(frame_comports, text=ports[i], height = 1, width = 40, font=('Helvetica', '12'),command = lambda: mySerial(6)).grid(row=6, column=0, padx=4, sticky ="W")
        i=i+1

def connectdb():
    global cnx
    global cursor

    try:
        cnx = mysql.connector.connect(user='bnajqrmy_balloon', password='MNSGCBallooning1!', host='50.87.136.197',
                                    database='bnajqrmy_andrew')
        cursor = cnx.cursor()

        # nodeLabels = ["One", "Two", "Three"]
        # # sql = "DROP TABLE sensorDataOne"
        # # cursor.execute(sql)
        #
        # for x in nodeLabels:
        #     sql = "DROP TABLE sensorData" + x
        #     cursor.execute(sql)
        #     createString = """CREATE TABLE sensorData""" + x + """(
        #     id int NOT NULL AUTO_INCREMENT,
        #     payload text,
        #     gpsDate text,
        #     gpsTime text,
        #     latitude text,
        #     longitude text,
        #     altitude text,
        #     sensor1 text,
        #     sensor2 text,
        #     sensor3 text,
        #     sensor4 text,
        #     sensor5 text,
        #     sensor6 text,
        #     PRIMARY KEY(id))"""
        #     print(createString)
        #     cursor.execute(createString)
        #     cnx.commit()

        # createString = """CREATE TABLE sensorDataOne (
        # id int NOT NULL AUTO_INCREMENT,
        # payload text,
        # gpsHour text,
        # gpsMin text,
        # gpsSecond text,
        # latitude text,
        # longitude text,
        # altitude text,
        # altGuess text,
        # intTemp text,
        # extTemp text,
        # PRIMARY KEY(id))"""
        # print(createString)
        #
        # cursor.execute(createString)
        # cnx.commit()

    except:
        print("didn't connect to database");

def writedb():
    global cnx
    global cursor
    try:
        # node.get()
        nodeLabels = ["One", "Two", "Three"]
        add_sensorData = ("INSERT INTO sensorData" + nodeLabels[node.get()-1] +
               "(payload, gpsDate, gpsTime, latitude, longitude, altitude, sensor1, sensor2, sensor3, sensor4, sensor5, sensor6) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        sensData = (str(fileList[0]), str(fileList[1]), str(fileList[2]), str(fileList[3]), str(fileList[4]), str(fileList[5]), str(fileList[6]), str(fileList[7]), str(fileList[8]), str(fileList[9]), str(fileList[10]), str(fileList[11]))
        cursor.execute(add_sensorData, sensData)
        cnx.commit()
    except:
        print("failed to post data")

def mySerial(number):
    currentPort = str(ports[number])
    global ser
    global k
    global comPort

    comPort = str(currentPort.split(' ')[0]) # Shortens the COM port + description (bluetooth, UART, etc.) to just the COM port

    ser.baudrate = 57600
    ser.port = comPort # Declare the serial we are using with the correct COM port
    ser.open() # open the serial port to receive data

    time.sleep(1) # delay for a second so we can clear the port

    openFile()
    retrieveData() # run more startup code

def openFile():
    global file
    global writer

    file = open(fileName,'w') # Open CSV file to write to
    ser.flushInput() # flush the input so there's no partial data strings

def updateMaps():
    global GPSpath
    if len(fileList) > 5:
        if fileList[4]!= 0:
            #Google_APIkey = "AIzaSyA3NXG_zuEHHv3gTRq0qzSIVcCJYOWrIDo"
            url = "https://maps.googleapis.com/maps/api/staticmap?"
            center = str(fileList[3]) + "," + str(fileList[4])
            GPSpath = GPSpath + "|" + center
            marker = "&markers=color:blue%7Clabel:M%7C" + center
            size = "&size=" + str(mapWidth) + "x" + str(mapHeight)
            try:
                fullURL = url + "center=" + center + "&zoom=" + str(mapZoom) + GPSpath + APRSpath + size + marker + APRSmarker + "&key=" + Google_APIkey
            except:
                fullURL = url + "center=" + center + "&zoom=" + str(mapZoom) + GPSpath + APRSpath + size + marker + "&key=" + Google_APIkey
            r = requests.get(fullURL)
            f = open("map.png", "wb")
            f.write(r.content)
            f.close()

            img.destroy()
            load = Image.open("map.png")
            render = ImageTk.PhotoImage(load)
            imgg = Label(frame_canvas, image=render)
            imgg.image = render
            imgg.grid(row=3, column=0, rowspan=2, columnspan = 2,sticky = 'nw', padx = 5, pady = 5)

    if(autoRefreshMap.get()==1):
        root.after(10000,updateMaps)

def retrieveData():
    global p
    global data
    global canvas
    global vsb
    global writer
    global headerList
    global fileList
    global frame_currentData
    global portsLength
    global currentTimeLabel

    if(ser.in_waiting > 2):

        frame_data.update_idletasks()
        recentData = ser.readline() # read last data line from the
        fileString = str(recentData).partition("!")[0] # eliminate exclamation mark and other characters associated with bowers xbee protocol
        fileString = fileString[fileString.find('b')+2:]
        fileString = fileString.replace(';',',')
        fileList = fileString.split(',') # split up the data string into a string list

        file.write(fileString + '\n')

        guiTime = datetime.datetime.now()

        # for z in range(len(fileList)):
        #     Label(frame_comports, text = headerList[z] + ": " + fileList[z] + "\t", font= ('Helvetica', '16'), bg = "maroon", fg= "white").grid(row=z+portsLength, column=0, sticky='nw')
        # Label(frame_comports, text = "Receive Time: " + str(guiTime.strftime('%H:%M:%S')), font= ('Helvetica', '16'), bg ="maroon", fg = "gold").grid(row = len(fileList)+portsLength+1, column=0, sticky='sw')

        checker = -1;

        for y in range(len(uniquePayloads)):
            if uniquePayloads[y] == fileList[0]:
                checker = y

        if checker == -1:
            try:
                uniquePayloads.append(fileList[0])
                fileTime = "Time" + today.strftime("%H-%M-%S") + "Payload" + fileList[0] +".csv" # create the file name in the "day folder" that is labeled with the exact time
                payloadFileName.append(os.path.join(fileDay, fileTime)) # merge folder and file
                payloadFile.append(open(payloadFileName[-1],'w'))
            except:
                pass

        try:
            payloadFile[checker].write(fileString + '\n')
        except:
            pass

        tabs = "\t"
        fileString = tabs.join(fileList) # make a new string seperated by tabs for GUI display
        data.append(fileString)

        if(p>=50):
            dataLabels[0].destroy()
            dataLabels.remove(dataLabels[0])

        dataLabels.append(Label(frame_data, text = data[p], font=('Helvetica', '10'),bg="white"))
        dataLabels[len(dataLabels)-1].grid(row=p,column=1) # write every single data string
        p = p + 1

        if(upload.get()==1): # checks to see if data upload checkbox is selected
            writedb()   # writes to server database if button is selected

        canvas.config(scrollregion=canvas.bbox("all"))
        if(scroll.get()==1):
            canvas.yview_moveto(1)

    guiTime = datetime.datetime.now()
    try:
        currentTimeLabel.destroy()
    except:
        pass
        #print("Current time failed to destroy")
    currentTimeLabel = Label(frame_comports, text = "Current Time: " + str(guiTime.strftime('%H:%M:%S')), font= ('Helvetica', '16'), bg ="maroon", fg = "gold")
    currentTimeLabel.grid(row = len(header)+portsLength+2, column=0, sticky='sw')
    root.after(100,retrieveData) # rerun function after this many ms

def send():
    try:
        toSend = str(payloadID.get()) + "?" + str(commandText.get()) + "!"
        toSendBytes = bytes(toSend, 'utf-8')
        ser.write(toSendBytes)
        print("sent: " + toSend)
    except:
        print("command send failed")

checkInternet()
initFiles()

frame_main = Frame(root,bg="maroon") # create a frame in root
frame_main.grid(sticky='news') # idk

Welcome = Label(frame_main, text = "MNSGC Ballooning", font=('Helvetica', '26'), bg="maroon", fg="white")
Welcome.grid(row=0, column=0, sticky = 'nw')

if internetConnection==True:
    connectionMessage = "Online"
else:
    connectionMessage = "Offline"

frame_internet = Frame(frame_main, bg = "maroon")
frame_internet.grid(row=1, column = 0, sticky = 'nw')

connectionLabel = Label(frame_internet, text = connectionMessage, font=('Helvetica', '16'), bg="maroon", fg="lightgray")
connectionLabel.grid(row=0, column=0, sticky = 'nw')

upload = IntVar() # variable that the checkbutton will control
if(internetConnection==True):
    upload.set(1)
dataUpload = Checkbutton(frame_internet, text="Upload to Server?", selectcolor = "black", bg="maroon", fg= "gold", font=('Helvetica', '12'), variable = upload)
dataUpload.grid(row=0,column=1, sticky = 'nw')

node = IntVar()
node.set(1)
Radiobutton(frame_internet, text="Node 1", font=('Helvetica', '14'), selectcolor = "black", bg="maroon", fg="lightgray", variable=node, value=1).grid(row=1,column=0, sticky = 'nw')
Radiobutton(frame_internet, text="Node 2", font=('Helvetica', '14'), selectcolor = "black", bg="maroon", fg="lightgray", variable=node, value=2).grid(row=2,column=0, sticky = 'nw')
Radiobutton(frame_internet, text="Node 3", font=('Helvetica', '14'), selectcolor = "black", bg="maroon", fg="lightgray", variable=node, value=3).grid(row=3,column=0, sticky = 'nw')

frame_APRS = Frame(frame_internet, bg = "maroon")
frame_APRS.grid(row=4, column=0, columnspan = 2)

callsignLabel = Label(frame_APRS, text= "Callsign: KD0AWK-", font=('Helvetica', '14'), bg="maroon", fg="lightgray")
callsignLabel.grid(row = 0, column=0, sticky = 'nw')

callsignNumber = Entry(frame_APRS, width = 5, font=('Helvetica', '14'), bg="white")
callsignNumber.grid(row = 0, column=1, sticky = 'nw')

useAPRS = Button(frame_APRS, text = 'load APRS data', font=('Helvetica', '12'), command = lambda: superposeAPRS())
useAPRS.grid(row = 0, column=2, padx = 5, columnspan = 3, sticky = 'nw')

frame_comports = Frame(frame_main, bg = "maroon")
frame_comports.grid(row=2, column = 0, sticky = 'nw')

frame_currentData = Frame(frame_main)
frame_currentData.grid(row=3, column = 0, columnspan = 2, sticky = 'nw')

frame_map = Frame(frame_main)
frame_map.grid(row=4, column=0, sticky = 'nw')

frame_canvas = Frame(frame_main) # create a new frame in the main frame
frame_canvas.grid(row=1, column=1, rowspan = 30, sticky='nw') # place the canvas rowspan = 10,
columns_width = 1200
rows_height = 300

label_canvas = Label(frame_main, text = header, height = 2, font=('Helvetica', '12'), bg="gold") # create a permanent header at the top of the GUI
label_canvas.grid(row=0, column=1, rowspan = 3, sticky='nw') # place the label

canvas = Canvas(frame_canvas, bg="white")
canvas.grid(row=0, column=0, sticky="news")
canvas.config(width = columns_width, height = rows_height)

vsb = Scrollbar(frame_canvas, orient="vertical", command = canvas.yview) # create a scroll bar in the text canvas
vsb.grid(row=0,column=1,sticky='ns') # Place the verical scroll bar

canvas.configure(yscrollcommand=vsb.set) # set the vertical scroll bar

frame_canvas.config(width=columns_width + vsb.winfo_width(), height= rows_height, bg="maroon")

frame_data = Frame(canvas,bg="white")
canvas.create_window((10,0), window=frame_data, anchor = 'nw')

scroll = IntVar() # variable that the checkbutton will control
scrollOrNot = Checkbutton(frame_canvas, text="Autoscroll", selectcolor = "black", bg="maroon", fg= "gold", font=('Helvetica', '14'), variable = scroll)
scrollOrNot.grid(row=1,column=0, sticky = 'ne')

frame_command = Frame(frame_canvas, bg = "maroon")
frame_command.grid(row = 2, column = 0, sticky = 'nw')

payloadIDLabel = Label(frame_command, text = "Payload ID:" ,  bg="maroon", fg= "gold", font=('Helvetica', '18')).grid(row=0, column=0, sticky="sw")
payloadID = Entry(frame_command, font=('Helvetica', '18'), width = 10)
payloadID.grid(row=0, column=1, sticky="sw")
commandLabel = Label(frame_command, text = "Command:" ,  bg="maroon", fg= "gold", font=('Helvetica', '18')).grid(row=0, column=2, sticky="sw")
commandText = Entry(frame_command,font=('Helvetica', '18'), width = 16)
commandText.grid(row=0, column=3, sticky="sw")
sendCommand = Button(frame_command, text = "SEND", font=('Helvetica', '12'), width = 10, command = lambda: send()).grid(row=0,column=4, padx = 5, sticky="sw")

img = Label(frame_canvas, text="no image yet")
img.grid(row=3, column=0, padx=5, pady=5, sticky='nw')

frame_zoom = Frame(frame_canvas, bg= "maroon")
frame_zoom.grid(row=5, column=0, sticky="nw")

mapRefresh = Button(frame_zoom, text = "Refresh Map", height = 1, width = 20, font=('Helvetica', '12'), command = lambda: myMap())
mapRefresh.grid(row=0, column=0, padx = 5, sticky="W")

mapZoomIn = Button(frame_zoom, text = "+", font=('Helvetica', '12'), command = lambda: zoomIn())
mapZoomIn.grid(row=0, column=1, padx = 0, pady=5, sticky="nw")

mapZoomOut = Button(frame_zoom, text = "-", font=('Helvetica', '12'), command = lambda: zoomOut())
mapZoomOut.grid(row=0, column=2, padx = 0, pady=5, sticky="nw")

autoRefreshMap = IntVar()
autoRefreshMap.set(0)
mapAutoRefresh = Checkbutton(frame_zoom, text="Auto Refresh every minute",  selectcolor = "black", bg="maroon", fg= "gold", font=('Helvetica', '12'), variable = autoRefreshMap)
mapAutoRefresh.grid(row=0, column=3, padx = 5, pady=5, sticky="nw")

choosePort()
connectdb()

root.mainloop()
