#!/usr/bin/python3
#coding:utf-8

import json
import base64

print ("Hello, Python!")

with open('./json3.txt','r+', encoding='UTF-8') as f:
    jsondata = json.load(f)
    jsonstr = json.dumps(jsondata)
    print(jsonstr)

header = 'ffff0001'
reserve = '0000'
tailer = '0000eeee'
datahex = base64.b16encode(jsonstr.encode())
datahexStr = datahex.decode('ascii')

length = '%04x' % len(jsonstr)
print('Data length: %d'%len(jsonstr))

output = header + length + reserve + datahexStr + tailer
print(output)


