#!/usr/bin/env python3

from netmiko import ConnectHandler
import argparse
import json
import os
import threading
import time
import zmq

parser = argparse.ArgumentParser()
parser.add_argument('--address', help='Set serving address and port for CSCC web service. Default: `140.114.87.87:5454`', default='140.114.87.87:5454', type=str)
parser.add_argument('--keepalive', help='Timeout(sec) ot send SSH/Telnet alive packet. Default: 60 secs.', default=60)
parser.add_argument('--check_duration', help='Timeout(sec) to check connection aliveness. Default: 5 secs.', default=5)
args = parser.parse_args()

# TODO: lock for each switch

class Lock:
  def __init__(self):
    self.lock = threading.Lock()
  
  def __enter__(self):
    self.lock.acquire()

  def __exit__(self, type, msg, traceback):
    if type:
      print(msg)
      print(traceback)
    self.lock.release()
    return False

threads = {}
end = False

def load_conf(path):
  if not os.path.exists(path):
    print('Config file %s not found.' % path)
    exit(1)

  with open(path, 'r') as f:
    config = json.loads(f.read())
    return config

def get_switch_config(switch):
  print('Getting running config from switch %s...' % switch['config']['ip'])
  connection = switch['connection']
  lock = switch['lock']
  with lock:
    if not connection.is_alive():
      connection = login(switch['config'])
      switch['connection'] = connection
  running_config = connection.send_command('show ru')

  print('Getting running config from switch %s... Success' % switch['config']['ip'])

  return running_config

def set_switch_interface_config(connection, interface_name, config):
  pass

def set_switch_accesslist(connection, acl_name, config):
  pass

def parse_config(running_config):
  running_config = running_config.split('\n')

  result = {'port': {}, 'acl': {}}

  conf = ''
  interface_name = ''
  acl_name = ''

  interface = False
  access_list = False

  i = 0
  while i < len(running_config):
    if 'interface' in running_config[i]:
      interface = True
      interface_name = running_config[i].split(' ')[1]
      i += 1
    elif 'ip access-list' in running_config[i]:
      access_list = True
      acl_name = running_config[i].split(' ')[-1]
      i += 1
    
    if interface:
      if running_config[i][0] == ' ':
        conf += running_config[i][1:] + '\n'
      else:
        result['port'][interface_name] = conf

        interface = False
        conf = ''

    if access_list:
      if running_config[i][0] == ' ':
        conf += running_config[i][1:] + '\n'
      else:
        result['acl'][acl_name] = conf
        access_list = False
        conf = ''

    i += 1

  return result

def login(config):
  device_type = 'cisco_ios'
  secret = config['secret']
  ip = config['ip']
  passwd = config['passwd']
  username = config['user']
  if config['type'] == 'telnet':
    device_type = 'cisco_ios_telnet'

  print('Connecting to %s...' % ip)
  con = ConnectHandler(
    device_type=device_type,
    host=ip,
    username=username,
    password=passwd,
    secret=secret,
    keepalive=args.keepalive
  )
  if secret:
    con.enable()

  print('Connecting to %s... Success' % ip)
  return con

def logout(switch):
  connection = switch['connection']
  lock = switch['lock']
  with lock:
    if connection.is_alive():
      connection.disconnect()
      print('Logout switch %s' % (switch['config']['ip']))
    else:
      print('Connection to switch %s has lost. Skip logout.' % switch['config']['ip'])

config = load_conf('config.json')
switches = {}
for switch_config in config['switch']:
  switch_ip = switch_config['ip']
  switches[switch_ip] = {
    'connection': login(switch_config),
    'config': switch_config,
    'lock': Lock()
  }

def watch_connection():
  while True:
    time.sleep(args.check_duration)
    if end:
      break
    for switch_ip, switch in switches.items():
      connection = switch['connection']
      with switch['lock']:
        if not connection.is_alive():
          print('Lost connection to switch %s. Trying to reconnect...' % switch_ip)
          connection = login(switch['config'])
          switch['connection'] = connection
          print('Lost connection to switch %s. Trying to reconnect... Success' % switch_ip)

def watch_command():
  '''
  Description:
    Watch command from IP management web.
  '''

  # Create zmq socket response side
  context = zmq.Context()
  socket = context.socket(zmq.REP)
  socket.bind('tcp://%s' % args.address)

  # Watch command and response
  while True:
    cmd = json.loads(socket.recv_string())
    if cmd['type'] == 'show all config':
      socket.send_string()

threads['watch_connection'] = threading.Thread(target=watch_connection)
threads['watch_connection'].start()

# Get initial running config from switch
# When administrator login management web, retrieve running config again
for switch_ip, switch in switches.items():
  running_config = get_switch_config(switch)

# Waiting for end
while not end:
  time.sleep(0.1)

# Join all threads
for _, t in threads.items():
  t.join()

# Logout all switch
for switch_ip, switch in switches.items():
  logout(switch)
