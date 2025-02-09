import socket
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
HOST = '34.121.82.35'
PORT = 40500

while True:
    wlan.connect('wifi_name', 'wifi_password')
    if wlan.isconnected() :
        print('wifi is connected')
        break
    else:
        print('Attemting to connect')
        time.sleep(5)
    
print(wlan.ifconfig()[0])
        
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST , PORT)) 
client.send(b'TEST')
message = client.recv(1024).decode()
print(message)
client.close()
