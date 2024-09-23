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
from mqtt_init import *  # Assuming you have some initialization here

# Creating Client name - should be unique 
global clientname
r = random.randrange(1, 10000000)
clientname = "IOT_client-Id-" + str(r)
relay_topic = 'daniella/boaz'
global ON
ON = False

class MqttClient():
    
    def __init__(self, clientname):
        self.clientname = clientname
        self.broker = ''
        self.port = '' 
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
    def set_publishMessage(self, value):
        self.publishMessage = value 
      
    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)
            
    def on_connect(self, client, userdata, flags, rc, a):
        if rc == 0:
            print(f"Client {self.clientname} connected OK")
            self.on_connected_to_form()            
        else:
            print(f"Client {self.clientname} Bad connection Returned code=", rc)
            
    def on_disconnect(self, client, userdata, flags, rc=0):
        print(f"Client {self.clientname} DisConnected result code " + str(rc))
            
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(f"Client {self.clientname} message from:" + topic, m_decode)
        
        # Update state for ConnectionDock1 if the topic is related to food
        if 'food' in topic:
            mainwin.connectionDock1.update_btn_state(topic, m_decode)
        
        # Update state for ConnectionDock2 if the topic is related to water
        elif 'water' in topic:
            mainwin.connectionDock2.update_btn_state(topic, m_decode)

    def connect_to(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print(f"Client {self.clientname} Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)
    
    def disconnect_from(self):
        self.client.disconnect()
    
    def start_listening(self):        
        self.client.loop_start()
    
    def stop_listening(self):        
        self.client.loop_stop()
    
    def subscribe_to(self, topic):        
        self.client.subscribe(topic)
              
    def publish_to(self, topic, message):
        self.client.publish(topic, message)

class ConnectionDock(QDockWidget):
    """Main """
    def __init__(self, mc, relay_number):
        QDockWidget.__init__(self)
        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.relay_number = relay_number
        self.relay_on = False  # State for the relay button
        
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)  # Ensure broker_ip is defined
        
        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)  # Ensure broker_port is defined
        
        self.eClientID = QLineEdit()
        self.eClientID.setText(mc.clientname)
        
        self.eUserName = QLineEdit()
        self.eUserName.setText(username)  # Ensure username is defined
        
        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)  # Ensure password is defined
        
        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")
        
        self.eSSL = QCheckBox()
        
        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)
        
        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("Click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")
        
        self.eSubscribeTopic = QLineEdit()
        self.eSubscribeTopic.setText(relay_topic + "/" + str(relay_number))

        self.ePushtbtn = QPushButton("", self)
        self.ePushtbtn.setToolTip("Push me")
        self.update_button_color()  # Initialize button color

        formLayout = QFormLayout()
        formLayout.addRow("Turn On/Off", self.eConnectbtn)
        formLayout.addRow("Sub topic", self.eSubscribeTopic)
        formLayout.addRow("Status", self.ePushtbtn)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle(f"Connect Relay {relay_number}")
        
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
        self.mc.subscribe_to(self.eSubscribeTopic.text())
    
    def update_btn_state(self, topic, message):
        if 'food' in topic:
            if 'relay_command: activate_low_food_relay' in message:
                self.relay_on = True
            elif 'relay_command: deactivate_low_food_relay' in message:
                self.relay_on = False
        elif 'water' in topic:
            if 'relay_command: activate_low_water_relay' in message:
                self.relay_on = True
            elif 'relay_command: deactivate_low_water_relay' in message:
                self.relay_on = False
        
        self.update_button_color()

    def update_button_color(self):
        if self.relay_on:
            self.ePushtbtn.setStyleSheet("background-color: red")
        else:
            self.ePushtbtn.setStyleSheet("background-color: gray")
      
class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
                
        # Init of MqttClient class for each relay
        self.mc1 = MqttClient("IOT_client-Id-1")
        self.mc2 = MqttClient("IOT_client-Id-2")
        
        # General GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # Set up main window
        self.setGeometry(30, 300, 600, 150)
        self.setWindowTitle('RELAY')        

        # Init QDockWidget objects        
        self.connectionDock1 = ConnectionDock(self.mc1, "food")
        self.connectionDock2 = ConnectionDock(self.mc2, "water")
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.connectionDock1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.connectionDock2)

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()