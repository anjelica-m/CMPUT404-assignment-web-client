#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        '''
        data - composed of headers and body. body is separated from headers by
        two newline characters, as demonstrated by the professor in eClass discussion forums (and notes).
        https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2340554
        '''
        #print("DATA IN CODE:", data)
        split_data = data.split("\n\n")
        #print("Data:", data)

        headers_all = split_data[0]

        headers_each = headers_all.split("\n")
        status = headers_each[0]
        #print("STATUS:", status)
        status_code = int(status.split(" ")[1]) # split into ["HTTP/1.1", code #, response]


        return status_code

    def get_headers(self,data):
        '''
        data - composed of headers and body. body is separated from headers by
        two newline characters, as demonstrated by the professor in eClass discussion forums (and notes).
        https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2340554
        '''
        header_content = {}

        split_data = data.split("\r\n\r\n")

        headers_all = split_data[0]
        headers = headers_all.split("\n")

        for each in headers:
            value = each.split(": ") # split between headers and the data, this should allow 'date' to be store properly
            header_content[each] = value
        
        #print("header content:", header_content)

        return header_content

    def get_body(self, data):
        '''
        data - composed of headers and body. body is separated from headers by
        two newline characters, as demonstrated by the professor in eClass discussion forums (and notes).
        https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2340554
        '''
    
        split_data = data.split("\r\n\r\n")
        #print("BODY SPLIT DATA:", split_data)
        if len(split_data) > 1:
            return split_data[1]
        else:
            return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        print("\n----GET Args----\n", args)
        '''
        METHOD path HTTP-version
        Host
        Accept?
        Accept-language?
        Connection
        '''
        #code = 500
        #body = ""
        #print(self.get_code)
        parsed_url = urllib.parse.urlparse(url)
        #print("Parse URL:", parsed_url)
        url_port = parsed_url.port
        host = parsed_url.hostname
        if url_port == None: # If no assigned port, assign 80 standard.
            url_port = 80 

        url_path = parsed_url.path
        if url_path == '':
            url_path = '/'

        self.connect(host, url_port)
        # GET request will have no 'body'
        # Accept: text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8
        send_payload = "GET "+str(url_path)+" HTTP/1.1\r\nUser-Agent: "+ "\r\nHost: "+ str(host) +"\r\nAccept: */*"+ "\r\nConnection: Close\r\n\r\n"
        print("SEND GET:", send_payload)
        self.sendall(send_payload)
        response = str(self.recvall(self.socket))
        self.close()

        body_content = self.get_body(response)
        response_code = self.get_code(response)

        #print("GET BODY RESP:",body_content)
        #print(response_code)
        #print("RESPONSE", body_content, response_code)
        return HTTPResponse(response_code, body_content)

    def POST(self, url, args=None):
        '''
        https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
        Example args: {'a': 'aaaaaaaaaaaaa', 'b': 'bbbbbbbbbbbbbbbbbbbbbb', 'c': 'c', 'd': '012345\r67890\n2321321\n\r'}
        -> since format of a dictionary, need to use urlencode!
        '''


        #print("\n----POST Args----\n", args)
        #code = 500
        #body = ""

        parsed_url = urllib.parse.urlparse(url)
        #print("Parse URL:", parsed_url)
        #print(parsed_url.port)
        if args is None:
            post_body = None
            content_length = 0
        else:
            post_body = urllib.parse.urlencode(args)
            content_length = len(post_body)

        url_port = parsed_url.port
        host = parsed_url.hostname
        if url_port == None: # If no assigned port, assign 80 standard.
            url_port = 80 

        url_path = parsed_url.path
        if url_path == '':
            url_path = '/'

        self.connect(host, url_port)

        if post_body == None:
            send_payload = "POST "+str(url_path)+" HTTP/1.1\nHost:"+ str(host) + "\nContent-Length: "+str(content_length)+"\nConnection: Close\n\n" + str(post_body) + "\n"
        else:
            send_payload = "POST "+str(url_path)+" HTTP/1.1\nHost:"+ str(host) + "\nContent-Length: "+str(content_length)+"\nContent-Type: "+"\nConnection: Close\n\n" + str(post_body) + "\n"
        #print("SEND POST:\n", send_payload)
        self.sendall(send_payload)
        response = str(self.recvall(self.socket))
        self.close()
        #print("POST RESPONSE", response)
        #print("trying to get body and code...")
        post_body = self.get_body(response)
        post_code = self.get_code(response)

        
        return HTTPResponse(post_code, post_body)

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
        
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        
        print(client.command( sys.argv[1] ))
