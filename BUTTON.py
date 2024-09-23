import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from mqtt_init import *
from db_manager import DatabaseManager

# Creating Client name - should be unique 
global clientname, CONNECTED
CONNECTED = False
r=random.randrange(1,10000000)
clientname="IOT_client-Id-"+str(r)

button_topic = 'daniella/boaz'


class Mqtt_client():
    
    def __init__(self):
        # broker IP adress:
        self.broker=''
        self.topic=''
        self.port='' 
        self.clientname=''
        self.username=''
        self.password=''        
        self.subscribeTopic=''
        self.publishTopic=''
        self.publishMessage=''
        self.on_connected_to_form = ''
        
    # Setters and getters
    def set_on_connected_to_form(self,on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    def get_broker(self):
        return self.broker
    def set_broker(self,value):
        self.broker= value         
    def get_port(self):
        return self.port
    def set_port(self,value):
        self.port= value     
    def get_clientName(self):
        return self.clientName
    def set_clientName(self,value):
        self.clientName= value        
    def get_username(self):
        return self.username
    def set_username(self,value):
        self.username= value     
    def get_password(self):
        return self.password
    def set_password(self,value):
        self.password= value         
    def get_subscribeTopic(self):
        return self.subscribeTopic
    def set_subscribeTopic(self,value):
        self.subscribeTopic= value        
    def get_publishTopic(self):
        return self.publishTopic
    def set_publishTopic(self,value):
        self.publishTopic= value         
    def get_publishMessage(self):
        return self.publishMessage
    def set_publishMessage(self,value):
        self.publishMessage= value 
        
        
    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)
            
    def on_connect(self ,client, userdata, flags, rc,a):
        global CONNECTED
        if rc==0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form();            
        else:
            print("Bad connection Returned code=",rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        CONNECTED = False
        print("DisConnected result code "+str(rc))
            
    def on_message(self, client, userdata, msg):
        topic=msg.topic
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        print("message from:"+topic, m_decode)
        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class        
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,self.clientname, clean_session=True) # create new client instance        
        self.client.on_connect=self.on_connect  #bind call back function
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self.on_log
        self.client.on_message=self.on_message
        self.client.username_pw_set(self.username,self.password)        
        print("Connecting to broker ",self.broker)        
        self.client.connect(self.broker,self.port)     #connect to broker
    
    def disconnect_from(self):
        self.client.disconnect()                   
    
    def start_listening(self):        
        self.client.loop_start()        
    
    def stop_listening(self):        
        self.client.loop_stop()    
    
    def subscribe_to(self, topic):
        if CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connecection should be established first")       
              
    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic,message)
        else:
            print("Can't publish. Connecection should be established first")         
      
class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self, mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        # Initialize the database manager
        self.db_manager = DatabaseManager()
        
        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)
        
        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)
        
        self.eUserName = QLineEdit()
        self.eUserName.setText(username)
        
        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)
        
        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL = QCheckBox()
        
        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        # Define new buttons
        self.eGiveFoodBtn = QPushButton("Give Food", self)
        self.eGiveFoodBtn.setToolTip("Give food if there is none in the bowl")
        self.eGiveFoodBtn.clicked.connect(self.give_food_click)
        
        self.eGiveWaterBtn = QPushButton("Give Water", self)
        self.eGiveWaterBtn.setToolTip("Give water if there is none in the water bowl")
        self.eGiveWaterBtn.clicked.connect(self.give_water_click)
        
        self.eGiveToyBtn = QPushButton("Give Toy", self)
        self.eGiveToyBtn.setToolTip("Give toy")
        self.eGiveToyBtn.clicked.connect(self.give_toy_click)
        
        self.eGiveSnackBtn = QPushButton("Give Snack", self)
        self.eGiveSnackBtn.setToolTip("Give snack")
        self.eGiveSnackBtn.clicked.connect(self.give_snack_click)

        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(button_topic)

        # Create a layout for the buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.eGiveFoodBtn)
        buttonLayout.addWidget(self.eGiveWaterBtn)
        buttonLayout.addWidget(self.eGiveToyBtn)
        buttonLayout.addWidget(self.eGiveSnackBtn)

        # Other buttons
        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("Click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")
        
        

        # Form layout
        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("Actions", buttonLayout) 

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connect") 
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()

    

    def give_food_click(self):
        # Add code to handle giving food
        resource_type = "food"
        resource = self.db_manager.get_resource(resource_type)
        
        if resource and resource[0] > 0:
            self.db_manager.update_resource(resource_type, resource[0] - 1)
            print("Giving food")
            self.mc.publish_to(self.ePublisherTopic.text(), "give_food")

            # Increase food level
            level_type = "food"
            level = self.db_manager.get_level(level_type)
            if level:
                self.db_manager.update_level(level_type, level[0] + 1)
                print(f"Food level increased to {level[0] + 1}")
        else:
            print("Not enough food!")

    def give_water_click(self):
        resource_type = "water"
        resource = self.db_manager.get_resource(resource_type)

        if resource and resource[0] > 0:
            self.db_manager.update_resource(resource_type, resource[0] - 1)
            print("Giving water")
            self.mc.publish_to(self.ePublisherTopic.text(), "give_water")

            # Increase water level
            level_type = "water"
            level = self.db_manager.get_level(level_type)
            if level:
                self.db_manager.update_level(level_type, level[0] + 1)
                print(f"Water level increased to {level[0] + 1}")
        else:
            print("Not enough water!")

    def give_toy_click(self):
        resource_type = "toys"
        resource = self.db_manager.get_resource(resource_type)

        if resource and resource[0] > 0:
            self.db_manager.update_resource(resource_type, resource[0] - 1)
            print("Giving toy")
            self.mc.publish_to(self.ePublisherTopic.text(), "give_toy")
        else:
            print("Not enough toys!")

    def give_snack_click(self):
        resource_type = "snacks"
        resource = self.db_manager.get_resource(resource_type)

        if resource and resource[0] > 0:
            self.db_manager.update_resource(resource_type, resource[0] - 1)
            print("Giving snack")
            self.mc.publish_to(self.ePublisherTopic.text(), "give_snack")
        else:
            print("Not enough snacks!")
        
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc=Mqtt_client()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 100, 300, 150)
        self.setWindowTitle('BUTTON')        

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)        
        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)


         # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set layout for central widget
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        
        # Add a label to central widget for display purposes
        self.label = QLabel("MQTT Client Ready")
        central_layout.addWidget(self.label)

        def closeEvent(self, event):
            self.connectionDock.db_manager.close()  # Close the database connection
            event.accept()  # Accept the event to close the window
       
app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
