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
r = random.randrange(1, 10000000)
clientname = "IOT_client-Id234-" + str(r)
DHT_topic = 'daniella/boaz'
update_rate = 10000  # in msec
food_threshold = 35
water_threshold = 35

class Mqtt_client():
    
    def __init__(self):
        self.broker = ''
        self.topic = ''
        self.port = '' 
        self.clientname = ''
        self.username = ''
        self.password = ''        
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''
        
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form
    
    def set_broker(self, value):
        self.broker = value         

    def set_port(self, value):
        self.port = value     
        
    def set_clientName(self, value):
        self.clientname = value        
    
    def set_username(self, value):
        self.username = value     
        
    def set_password(self, value):
        self.password = value         
    
    def set_subscribeTopic(self, value):
        self.subscribeTopic = value        
    
    def set_publishTopic(self, value):
        self.publishTopic = value         

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)
            
    def on_connect(self, client, userdata, flags, rc, a):
        global CONNECTED
        if rc == 0:
            print("connected OK")
            CONNECTED = True
            self.on_connected_to_form()            
        else:
            print("Bad connection Returned code=", rc)
            
    def on_disconnect(self, client, userdata, flags, rc, a):
        CONNECTED = False
        print("DisConnected result code " + str(rc))
            
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        
        # Handle message for specific relay actions
        if 'food' in topic:
            if 'activate_food' in m_decode:
                mainwin.connectionDock.update_mess_win('food', 'activate')
            elif 'deactivate_food' in m_decode:
                mainwin.connectionDock.update_mess_win('food', 'deactivate')
        
        if 'water' in topic:
            if 'activate_water' in m_decode:
                mainwin.connectionDock.update_mess_win('water', 'activate')
            elif 'deactivate_water' in m_decode:
                mainwin.connectionDock.update_mess_win('water', 'deactivate')

    def connect_to(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)
    
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
            print("Can't subscribe. Connection should be established first")
    
    def publish_to(self, topic, message):
        if CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connection should be established first")          


class ConnectionDock(QDockWidget):
    def __init__(self, mc):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)
        
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
        
        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")
        
        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(DHT_topic)

        self.FoodLevel = QLineEdit()
        self.FoodLevel.setText('')

        self.WaterLevel = QLineEdit()
        self.WaterLevel.setText('')

        formLayout = QFormLayout()
        formLayout.addRow("Turn On/Off", self.eConnectbtn)
        formLayout.addRow("Pub topic", self.ePublisherTopic)
        formLayout.addRow("Food Level", self.FoodLevel)
        formLayout.addRow("Water Level", self.WaterLevel)

        widget = QWidget(self)
        widget.setLayout(formLayout)
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

    def push_button_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), '"value":1')
     
    def update_mess_win(self, relay, action):
        if relay == 'food':
            if action == 'activate':
                self.eConnectbtn.setStyleSheet("background-color: red")  # Active state
            elif action == 'deactivate':
                self.eConnectbtn.setStyleSheet("background-color: gray")  # Deactivated state
        elif relay == 'water':
            if action == 'activate':
                self.eConnectbtn.setStyleSheet("background-color: blue")  # Active state
            elif action == 'deactivate':
                self.eConnectbtn.setStyleSheet("background-color: gray")  # Deactivated state

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of Mqtt_client class
        self.mc = Mqtt_client()

        # Initialize DatabaseManager
        self.db_manager = DatabaseManager()

        # Get initial food and water levels
        self.food_level = self.db_manager.get_level("food")[0] if self.db_manager.get_level("food") else 38
        self.water_level = self.db_manager.get_level("water")[0] if self.db_manager.get_level("water") else 38

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate) # in msec
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 600, 300, 150)
        self.setWindowTitle('Food and Water Levels')        

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)        
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        

    def update_data(self):
        self.food_level = self.db_manager.get_level("food")[0] if self.db_manager.get_level("food") else 38
        self.water_level = self.db_manager.get_level("water")[0] if self.db_manager.get_level("water") else 38
        print('Next update')

        # Decrease levels
        if self.food_level > 0:
            self.food_level -= 1
        if self.water_level > 0:
            self.water_level -= 1

        # Update the UI
        self.connectionDock.FoodLevel.setText(str(self.food_level))
        self.connectionDock.WaterLevel.setText(str(self.water_level))

        # Publish current data
        current_data = f'Food Level: {self.food_level} Water Level: {self.water_level}'
        self.mc.publish_to(DHT_topic, current_data)

        # Save levels to database
        self.db_manager.update_level("food", self.food_level)
        self.db_manager.update_level("water", self.water_level)

        # Activate or deactivate relay based on food and water levels
        if self.food_level < food_threshold:
            self.mc.publish_to(DHT_topic+"/"+"food", 'relay_command: activate_low_food_relay')
        else:
            self.mc.publish_to(DHT_topic+"/"+"food", 'relay_command: deactivate_low_food_relay')

        if self.water_level < water_threshold:
            self.mc.publish_to(DHT_topic+"/"+"water", 'relay_command: activate_low_water_relay')
        else:
            self.mc.publish_to(DHT_topic+"/"+"water", 'relay_command: deactivate_low_water_relay')

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()