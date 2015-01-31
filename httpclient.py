#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 Paul Nhan, Jessica Surya
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# CMPUT 410 Winter 2015 Assignment Submission
# Due: February 2. 2015
# Original assignment creator: Abram Hindle
# Assignment Contributors: Paul Nhan (pnhan), Jessica Surya (jsurya)

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):

    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        try:
            remote_ip = socket.gethostbyname(url)
            print 'Ip address of ' + url + ' is ' + remote_ip
            return remote_ip

        except socket.gaierror:
            # Could not resolve IP
            print 'Hostname could not be resolved... Exiting'
            sys.exit()           

    def connect(self, host, port):
        # use sockets!
        try:
        # Create an AF_INET, STREAM socket (TCP)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit()
 
        print 'Socket Created'
        # Connect to remote server
        remote_ip = self.get_host_port(host)
        s.connect((remote_ip, port))
        print 'Socket Connected to ' + host + ' on ip ' + remote_ip
        return s

    def get_code(self, data):
        # Identify HTTP Return Code
        index = data.find("\r\n")
        fragment = data[:index]
        fragment = fragment.split(" ")
        code =  int(fragment[1])
        return code

    def get_headers(self,data):
        # Parse HTTP Return Header
        index = data.find("\r\n\r\n")
        headers = data[0:index]
        return headers

    def get_body(self, data):
        # Parse HTTP Return Content
        index = data.find("\r\n\r\n")
        body = data[index:]
        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def get_params(self, url):
        params = url.split(':')
        host = ""
        path = ""
        port = 80
        # Extract host, path, and port from URL
        if len(params) > 2:
            # Port is specified
            host = params[1][2:]
            path = params[-1]

            if "/" in path:
                port_end = path.find('/')
                port_string = path[:port_end]
                path = path[port_end:]
                port = int(port_string)
            else:
                port_string = int(path)
                path = ""

        else:
            # Port is not specified; defaults to port 80
            host = params[1][2:]
            if "/" in host:
                host_end = host.find("/")
                host = host[:host_end]
                path = host[host_end:]
            else:
                host = host
                path = ""
        # print host
        # print path
        # print port

        return host, path, port

    def GET(self, url, args=None):
        host, path, port = self.get_params(url)

        # Connect to specified host
        s = self.connect(host, port)
        message = "GET /" + path + " HTTP/1.1\r\nHost: " + host + "\r\nAccept:*/*\r\nConnection:close\r\n\r\n"

        try:
            s.sendall(message)
        except socket.error:
            print("Sending data failed")
            sys.exit()

        data = self.recvall(s)
        code = self.get_code(data)
        header = self.get_headers(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, path, port = self.get_params(url)

        # Connect to specified host
        s = self.connect(host, port)

        if args != None:
            encoding = urllib.urlencode(args)
        else:
            encoding = ''

        message = "POST /" + path +  " HTTP/1.1\r\nHost: " + host + "\r\nAccept: */*\r\nContent-Length: " + str(len(encoding)) + "\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n" + encoding

        try:
            s.sendall(message)
        except socket.error:
            print("Sending data failed")
            sys.exit()

        data = self.recvall(s)
        code = self.get_code(data)
        header = self.get_headers(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        # arguments flipped to comply with  project specifications
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        # arguments flipped to comply with  project specifications
        print client.command( sys.argv[1], command )    
