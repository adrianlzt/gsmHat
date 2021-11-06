#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
Incomplete simulator for Civlo85/gsmHat
Modified from http://allican.be/blog/2017/01/15/python-dummy-serial-port.html
"""

import os, pty
from serial import Serial
import threading
import requests
from datetime import datetime

latitude = b"45.181295"
longitude = b"5.736763"

def listener(port):
    # To store requests
    http_request = None

    #continuously listen to commands on the master device
    while 1:
        res = b""
        while not res.endswith(b"\n"):
            #keep reading one byte at a time until we have a full line
            res += os.read(port, 1)

        #print("command: %s" % res)

        #write back the response
        if res == b'AT+CMGF=1\n':
            os.write(port, b"AT+CMGF=1\n")
            os.write(port, b"OK\n")
        elif res == b'AT+CPMS="SM"\n':
            os.write(port, b'AT+CPMS="SM"\n')
            os.write(port, b"+CPMS: 0,10,0,10,0,10\n")
            os.write(port, b"OK\n")
        elif res == b'AT+CGNSPWR=1\n':
            os.write(port, b'AT+CGNSPWR=1\n')
            os.write(port, b"OK\n")
        elif res == b'AT+CGNSTST=0\n':
            os.write(port, b"AT+CGNSTST=0\n")
            os.write(port, b"OK\n")
        elif res == b'AT+CGNSINF\n':
            os.write(port, b"AT+CGNSINF\n")
            # Return always the same coordinates but with different timestamp
            os.write(port, b"+CGNSINF: 1,1,%s.000,%s,%s,192.407,0.00,0.0,1,,1.0,2.3,2.1,,8,11,,,52,,\n" % (bytes(datetime.now().strftime("%Y%m%d%H%M%S").encode()), latitude, longitude))
            os.write(port, b"OK\n")
        elif res == b'AT+SAPBR=2,1\n':
            os.write(port, b"AT+SAPBR=2,1\n")
            # Return the IP 10.2.2.2.
            os.write(port, b'+SAPBR: 1,3,"10.2.2.2"\n')
            os.write(port, b"OK\n")
        elif res == b'AT+SAPBR=3,1,"Contype","GPRS"\n':
            os.write(port, b'AT+SAPBR=3,1,"Contype","GPRS"\n')
            os.write(port, b'\n')
            os.write(port, b"OK\n")
        elif res == b'AT+SAPBR=3,1,"APN","TM"\n':
            os.write(port, b'AT+SAPBR=3,1,"APN","TM"\n')
            os.write(port, b"OK\n")
        elif res == b'AT+SAPBR=3,1,"USER",""\n':
            os.write(port, b'AT+SAPBR=3,1,"USER",""\n')
            os.write(port, b"OK\n")
        elif res == b'AT+SAPBR=3,1,"PWD",""\n':
            os.write(port, b'AT+SAPBR=3,1,"PWD",""\n')
            os.write(port, b"OK\n")
        elif res == b'AT+SAPBR=1,1\n':
            os.write(port, b'AT+SAPBR=1,1\n')
            os.write(port, b"+CGNSPWR: 1\n")
            os.write(port, b'+CTZV: +4,0\n')
            os.write(port, b'*PSUTTZ: 2021,11,5,8,5,26,"+4",0\n')
            os.write(port, b'DST: 0\n')
            os.write(port, b'+CIEV: 10,"20801","Orange F","Orange F", 0, 0\n')
            os.write(port, b"OK\n")
        elif res == b'AT+HTTPINIT\n':
            os.write(port, b'AT+HTTPINIT\n')
            os.write(port, b'OK\n')
        elif res == b'AT+HTTPPARA="TIMEOUT",540\n':
            os.write(port, b'AT+HTTPPARA="CID",1\n')
            os.write(port, b'OK\n')
        elif res == b'AT+HTTPPARA="CID",1\n':
            os.write(port, b'AT+HTTPPARA="CID",1\n')
            os.write(port, b'OK\n')
        elif res.startswith(b'AT+HTTPPARA="URL","'):
            url = res.split(b'"')[3]
            print(f"http request: {url.decode()}")
            os.write(port, b'AT+HTTPPARA="URL","%s"\n' % url)
            os.write(port, b'OK\n')
            http_request = requests.get(url, headers={"User-Agent": "SIMCOM_MODULE"})
        elif res == b'AT+HTTPACTION=0\n':
            os.write(port, b'AT+HTTPACTION=0\n')
            os.write(port, b'OK\n')
            # Send the message that the request is ready
            os.write(port, b'+HTTPACTION: 0,%d,1\n' % http_request.status_code)
        elif res == b'AT+HTTPREAD\n':
            os.write(port, b'AT+HTTPREAD\n')
            os.write(port, b'+HTTPREAD: 1\n')
            print(f"http response (code {http_request.status_code}): {http_request.text}")
            #os.write(port, b"0\n")
            os.write(port, b"%s\n" % bytes(http_request.text.encode()))
            os.write(port, b'OK\r\n')
        elif res == b'AT+HTTPTERM\n':
            os.write(port, b'AT+HTTPTERM\n')
            os.write(port, b'OK\n')
        else:
            print(f"Unknown command: {res}")

def main():
    """Start the testing"""
    master,slave = pty.openpty() #open the pseudoterminal
    s_name = os.ttyname(slave) #translate the slave fd to a filename
    print(f"point gsmHat to this device: {s_name}")
    listener(master)

if __name__=='__main__':
    main()
