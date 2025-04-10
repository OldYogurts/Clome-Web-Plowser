#!/usr/bin/env python3


import socket
import ssl
import sys
import tkinter
from dataclasses import dataclass
#     < URL CLASS>

class URL:
    def __init__(self,url):

        
        self.scheme,url = url.split(':',1);
        self.view_src = 0;
        assert self.scheme in ['http','https','file','data','view-source'];
        if self.scheme == 'view-source':
            self.view_src = 1;
            self.scheme,url = url.split(':',2)
        if self.scheme in ["http",'https']: url =url.replace("//" , "")
        if self.scheme == 'http': self.port = 80;
        elif self.scheme == 'https':self.port = 443;
        #TODO : this just wont work mate
        elif self.scheme == 'file': open("{}".format(url),'r')
        # TODO : make this good man wtf
        elif self.scheme == 'data':

            lang_type = url.split("/",1)[1].split(',',1)[0]
            text = url.split(",",1)[1]
            self.lang_type,self.text  = lang_type,text
        if '/' not in url:
            url = url + '/';
        self.host,url = url.split('/',1);
        if ':' in self.host and self.scheme in ['http','https']:
            self.host,port = self.host.split(':',1);
            self.port = int(port);
        self.path = '/'+url;
        
    def request(self):
            s = socket.socket(family=socket.AF_INET,
                              type=socket.SOCK_STREAM,
                              proto=socket.IPPROTO_TCP)
            s.connect((self.host,self.port));#takes in only 1 list arg ((host,port)).
            if self.scheme == 'https':
               ctx = ssl.create_default_context();
               s = ctx.wrap_socket(s,server_hostname = self.host)
            req_dict = {"HOST:":self.host,"User-Agent:":"Tyrannosaurus Sex!","Connection:":"keep-alive"}
            request = "GET {} HTTP/1.1\r\n".format(self.path)
            for k,v in req_dict.items():
                request += "{} {} \r\n".format(k,v)
            request += "\r\n"
            print(f"REQUEST SEND\n\n*** \n{request}\n***")
            s.send(request.encode("utf8")) #send request must be  encode str in bytes
            #get server response:
            response = s.makefile("r" ,encoding = "utf8",errors ="strict",newline ="\r\n")
            #parse response of status:
            statusLine = response.readline()
            print(f"STATUSLINE\n\n***\n{statusLine}\n***")
            version,status,message = statusLine.split(" ",2);
            #parse all other headers:
            response_headers = {};
            while True:
                line = response.readline();
                if line == "\r\n": break;
                #of type HEADER : VALUE 
                header , value = line.split(":",1);
                response_headers[header.casefold()] = value.strip(); #strip cuz " " useless
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
            if int(status) >=300 and int(status)< 400:
                redirections ='"'+ response_headers["location"]+'"'
                self.redir = redirections
                return self.redir
            print(response_headers)
            content = response.read(int(response_headers['content-length']));
            s.close();
            return content
    

           
            #</URL CLASS >
            #<BROWSER CLASS>
class Browser:
    def __init__(self):
        self.scroll = 0;
        self.window = tkinter.Tk();
        self.window.bind("<s>",self.scrolldown);
        self.window.bind("<w>",self.scrollup);
        self.canvas = tkinter.Canvas(
                self.window,
                width = WIDTH,
                height = HEIGHT
                )
        self.canvas.pack();

    def draw(self):
        self.canvas.delete("all")
        for x,y,word,font in self.display_list:
            if y > self.scroll + HEIGHT: continue;
            if y + VSTEP < self.scroll: continue;

            self.canvas.create_text(x,y-self.scroll,text = word,font=font);
    def scrolldown(self,a):
        self.scroll += SCROLLSTEP;
        self.draw();
    def scrollup(self,a):
        self.scroll -= SCROLLSTEP;
        self.draw();
    def load(self,url):
         
     #   if "redirect" in url.path:

        if url.scheme not in ["data","file"]:
            body = url.request()
        if url.view_src == 0:
                print("Connected")
                tokens = lex(body)
        

        elif url.view_src ==1:
                print("view page source")
                text=view_source(body)
        elif url.scheme == "data":
            
                lang = url.lang_type
                text = url.text
                text = text.replace("&lt;","<")
                text = text.replace("&gt;",">")
        self.display_list = Layout(tokens).display_list;
        self.draw();

# *** TEXT ONTS AND TYPES MANAGER CLASSES***

WIDTH,HEIGHT = 800,600;
HSTEP , VSTEP = 13,18
SCROLLSTEP = 60;

import tkinter.font

class Layout:
    def __init__(self,tokens):
        self.display_list =[]
        
        self.cursor_x , self.cursor_y = HSTEP,VSTEP;
        self.size , self.weight   , self.style    = 16 ,"normal", "roman";
        for tok in tokens:
            self.Token(tok);
    def Token(self,tok):
            if isinstance(tok , Text):
               for word in tok.text.split():
                  font = tkinter.font.Font(
                                            size=self.size,
                                            weight=self.weight,
                                            slant=self.style
                                            )
                                   
                  w=font.measure(word);
            
                  if self.cursor_x + w > WIDTH - HSTEP:
                        self.cursor_y += font.metrics("linespace") *1.5 ;
                        self.cursor_x = HSTEP
                  wrd_tpl = (self.cursor_x,self.cursor_y,word,font)
                  self.display_list.append(wrd_tpl);
                  self.cursor_x += w + font.measure(" ");


            elif tok.tag == "i":
                 style = "italic";
            elif tok.tag == "b":
                 weight = "bold";
            elif tok.tag =="/i":
                 style = "roman";
            elif tok.tag == "/b":
                 weight = "normal"
            return self.display_list;


@dataclass
class Text:
    text : str;
@dataclass
class Tag:
    tag : str;
#LEX METHOD
def lex(body):

    out = []
    buffer = ""
    in_tag = False
    
    for c in body:
            if c == "<": 
                in_tag = True 
                if buffer :out.append(Text(buffer));
                buffer = ""
            elif c == ">":
                in_tag = False
                out.append(Tag(buffer));
                buffer = "";   
            else:
                buffer +=c
    if not in_tag and buffer:
                out.append(Text(buffer));
    return out;
#HELPER METHODS:
def view_source(body):
    text = ""
    for c in body :
        text += c
    return text;


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
