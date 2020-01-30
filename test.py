#!/usr/bin/env python3
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:5454')

socket.send_string(json.dumps({
  'type': 'show config',
  'switch_ip': '192.168.127.23'
}))
print(socket.recv_string())
socket.close()
