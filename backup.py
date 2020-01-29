#!/usr/bin/env python3

from netmiko import ConnectHandler
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import re
import threading
import time

parser = argparse.ArgumentParser(description='Backup switch settings.')
parser.add_argument('config', help="Path to configure file. Info about switch will be stored here.")
parser.add_argument('backup_path', help="Path to backup folder. All switch setting will be saved to this folder.")
args = parser.parse_args()

def load_conf(path):
  if not os.path.exists(path):
    print('Config file %s not found.' % path)
    exit(1)

  with open(path, 'r') as f:
    config = json.loads(f.read())
    return config

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
    keepalive=1
  )
  if secret:
    con.enable()

  print('Connecting to %s... Success' % ip)
  return con

def check_redundancy(path):
  hashes = {}
  toRemove = []
  dirs = sorted([dir for dir in os.listdir(path) if os.path.isdir(path + '/' + dir)], reverse=True)
  if len(dirs) < 1:
    return
  files = os.listdir(path + '/' + dirs[0])

  # Calculate latest hash
  for fn in files:
    with open(path + '/' + dirs[0] + '/' + fn, 'rb') as fp:
      content = fp.read()
    hash = hashlib.sha256(content).hexdigest()
    hashes[fn] = hash

  # Find previous file
  allFiles = set(list(hashes.keys()))
  preFiles = set()
  preFilePath = []
  for dir in dirs[1:]:
    curPath = path + '/' + dir
    curFiles = set(os.listdir(curPath))
    toAddFiles = (allFiles - preFiles) & curFiles
    preFilePath += [path + '/' + dirs[0] + '/' + fn for fn in toAddFiles]
    preFiles = preFiles | curFiles
  
  # Calculate hash of previous file
  for path in preFilePath:
    with open(path, 'rb') as fp:
      content = fp.read()
    hash = hashlib.sha256(content).hexdigest()
    path = path.split('/')
    filename = path[-1]
    dirname = '/'.join(path[:-1])
    if hash == hashes[filename]:
      print('/'.join(path))
      os.remove('/'.join(path))
      if len(os.listdir(dirname)) == 0:
        print(dirname)
        os.rmdir(dirname)

def backup(switch_config):
  switch_ip = switch_config['ip']
  switches[switch_ip] = {
    'connection': login(switch_config),
    'config': switch_config
  }
  connection = switches[switch_ip]['connection']
  sh_ru = connection.send_command('sh ru').split('\n')
  sh_ru = [line for line in sh_ru if 'ntp clock-period' not in line]
  sh_int_des = connection.send_command('show int des').split('\n')
  sh_int_des = [re.sub(r'\s+', ' ', line).split(' ', 3) for line in sh_int_des]
  sh_int_des = [[line[0], line[3]] for line in sh_int_des]
  date = time.strftime("%Y-%m-%d-%H", time.localtime())
  with open(args.backup_path + '/%s/%s.log' % (date, switch_ip), 'w') as fp:
    json.dump({'sh_ru': sh_ru, 'sh_int_des': sh_int_des}, fp)
  connection.disconnect()

if not os.path.isdir(args.backup_path):
  os.mkdir(args.backup_path)

config = load_conf(args.config)
switches = {}

while True:
  if int(time.time()) % 3600 == 0:
    date = time.strftime("%Y-%m-%d-%H", time.localtime())
    if not os.path.isdir(args.backup_path + '/' + date):
      print('> Backup at %s...' % date)
      os.mkdir(args.backup_path + '/' + date)
      pool = mp.Pool(len(config['switch']))
      pool.map(backup, config['switch'])
      pool.close()
      pool.join()
      print('> Backup at %s... Done' % date)
      check_redundancy(args.backup_path)

  t = 3600 - time.time() % 3600
  print('\r> Next backup time: %02d:%02d ' % (t // 60, t % 60), end='')
  time.sleep(0.5)
