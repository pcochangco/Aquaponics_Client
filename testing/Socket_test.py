# -*- coding: utf-8 -*-
"""
Created on Sep 23 13:35:41 2021

@author: pcochangco
"""
#!/usr/bin/env python3

import socket
import time

HOST = '172.20.10.7'  # The server's hostname or IP address
PORT = 65432        # The port used by the server


def lettuceArea():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:
            try:
                print("Trying to Connect to server..")
                s.connect((HOST, PORT))
                print("Connected!")
                break
            except Exception as e:
                print(e)
                time.sleep(1)
        s.sendall(str.encode('Requesting to send the lettuce area'))
        while True:
            try:
                print("Waiting to receive the from Server")
                data = s.recv(1024)
                print("Data received from Server, Lettuce Area:", data.decode('utf-8'))
                break
            except Exception as e:
                print(e)
                time.sleep(1)
            
    return int(data.decode('utf-8'))

print(lettuceArea())
