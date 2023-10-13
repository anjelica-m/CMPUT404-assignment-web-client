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

# GET and POST Written By: Anjelica Marianicz (ccid: anjelica)

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

RN = '\r\n'

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

        Code follows directly after HTTP/1.1 in the data.
        '''
        split_data = data.split(RN+RN)

        headers_all = split_data[0]

        headers_each = headers_all.split(RN)
        status = headers_each[0] # The code appears in the first line of the headers block.
        status_code = status.split(" ") # split into ["HTTP/1.1", code #, response, so [1] is the code.
        status_code = int(status_code[1]) 


        return status_code

    def get_headers(self,data):
        '''
        data - composed of headers and body. body is separated from headers by
        two newline characters and two \r (moves cursor back to beginning of the line), as demonstrated by the professor in eClass discussion forums (and notes).
        https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2340554
        '''
        header_content = {} # Dictionary to store Header : Header-Content pairs.

        split_data = data.split(RN+RN)

        headers_all = split_data[0] # All headers in one block.
        headers = headers_all.split(RN) # all headers separated by \r\n character.

        for each in headers:
            value = each.split(": ") # split between headers and the data, this should allow 'date' to be store properly
            header_content[each] = value
        
        #print("header content:", header_content)

        return header_content

    def get_body(self, data):
        '''
        data - composed of headers and body. body is separated from headers by
        two newline characters and two \r (moves cursor back to beginning of the line), as demonstrated by the professor in eClass discussion forums (and notes).
        https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2340554

        See reference 6).
        '''
    
        split_data = data.split(RN+RN)

        if len(split_data) > 1: # This indicates there is body in the data to be grabbed. If length is not mroe than 1, there is no body.
            return split_data[1]
        else:
            return None
    
    def sendall(self, data):
        # Completed for us.
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        # Completed for us.
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
        #print("\n----GET Args----\n", args)
        '''
        Format of the payload that needs to be sent:
        METHOD path HTTP-version
        headers needed:
        Host:
        Accept:
        Connection:
        '''
        
        parsed_url = urllib.parse.urlparse(url)
        url_port = parsed_url.port
        host = parsed_url.hostname
        if url_port == None: # If no assigned port, assign 80 standard HTTP.
            url_port = 80 

        url_path = parsed_url.path
        # print("PATH", url_path), some paths are simply '', need to set to '/'. Like in Assignment1.
        if url_path == '':
            url_path = url_path + '/'


        self.connect(host, url_port)
        # GET request will have no 'body'
        accept = 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8' # From mdn web docs
        send_data = "GET "+str(url_path)+" HTTP/1.1" +RN+ "Host: "+ str(host) +RN+"Accept: " + accept +RN+ "Connection: Close"+RN+RN
        self.sendall(send_data) # Send client request.
        response = str(self.recvall(self.socket)) # Receive the response form the server.
        self.close() # Close the connection.

        body_content = self.get_body(response)
        response_code = self.get_code(response)

        return HTTPResponse(response_code, body_content)

    def POST(self, url, args=None):
        #print("\n----POST Args----\n", args)
        '''
        https://docs.python.org/3/library/urllib.parse.html#module-urllib.parse
        Example args printout: {'a': 'aaaaaaaaaaaaa', 'b': 'bbbbbbbbbbbbbbbbbbbbbb', 'c': 'c', 'd': '012345\r67890\n2321321\n\r'}
        -> since format of a dictionary, need to use urlencode!

        According to tests:
        headers needed:
        Host:
        Content-Length:
        Content-Type:
        '''

        parsed_url = urllib.parse.urlparse(url)
        if args is None:
            # No information is passed to the function, set these parameters to 0.
            post_body = None
            content_length = 0
        else:
            post_body = urllib.parse.urlencode(args)
            content_length = len(post_body)

        url_port = parsed_url.port
        host = parsed_url.hostname
        if url_port == None: # If no assigned port, assign 80 standard HTTP.
            url_port = 80 

        url_path = parsed_url.path
        if url_path == '':
            url_path = url_path + '/'

        self.connect(host, url_port)

        if post_body == None:
            send_data = "POST "+str(url_path)+" HTTP/1.1"+RN+"Host:"+ str(host) +RN+ "Content-Length: "+str(content_length)+RN+"Connection: Close" +RN+RN+ str(post_body) + RN
        else:
            send_data = "POST "+str(url_path)+" HTTP/1.1"+RN+"Host:"+ str(host) +RN+ "Content-Length: "+str(content_length)+RN+"Content-Type: "+RN+"Connection: Close" +RN+RN+ str(post_body) + RN
        
        self.sendall(send_data) # Send the client request.
        response = str(self.recvall(self.socket)) # Receive the response from the server.
        self.close() # Close the connection.
        response_body = self.get_body(response)
        response_code = self.get_code(response)

        return HTTPResponse(response_code, response_body)

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
