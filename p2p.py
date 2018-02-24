#! /usr/bin/env python

import socket
import sys
import time
import threading
import select
import fcntl
import struct
from netaddr import IPAddress, IPNetwork
import signal
import commands

listaIPValidas = []
listaIPUso = []
lista_socket = []

class GetNodes(threading.Thread):

    def run(self):
        #Obtener IP local
        iface = commands.getoutput('ls /sys/class/net | grep wl')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipLocal = str(s.getsockname()[0])
        print ipLocal
        s.close()

        #Obtener mascara de subnet
        subnetMask = str (IPAddress(socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', str(iface)))[20:24])).netmask_bits())
        print subnetMask

        #Obtener lista de hosts de la subnet actual
        listaIPs = []
        for ip in IPNetwork(ipLocal + "/" + subnetMask):
            listaIPs.append('%s' % ip)

        #now connect to the web server on port 80
        # - the normal http port

        while True:
            for ip in listaIPs:
                try:
                    if (ip!=ipLocal and not(ip in listaIPValidas)):
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.1)
                        s.connect((ip, 8999))
                        s.close()
                        #print ip, 'Se conecto exitosamente'
                        listaIPValidas.append(ip)
                        #listaIPUso.append(ip)
                    pass
                except:
                    #print ip, 'No esta disponible'
                    pass 
                pass
            
        #print listaIPValidas
        


class Server(threading.Thread):
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Server started successfully\n"
        hostname = ''
        port = 8999
        self.sock.bind((hostname, port))
        self.sock.listen(1)
        print "Listening on port %d\n" % port
        # time.sleep(2)

        lista_socket.append(self.sock)

        while 1:

            lectura, escritura, error_in = select.select(lista_socket, [], [], 0)

            for sock in lectura:

                if sock == self.sock:
                    connessione, addr = self.sock.accept()
                    lista_socket.append(connessione)
                    
                    print "El Cliente [%s, %s] se conecto!" % addr
                    cli = Client()
                    print "Started successfully"
                    cli.start()

            else:

                try:
                    data = sock.recv(4096)
                    if data:
                        print "[" + str(sock.getpeername()) + "]" + " > " + data
                    else:
                        if sock in lista_socket:
                            lista_socket.remove(sock)
                except:
                    continue
        self.sock.close()


class Client(threading.Thread):


    def connect(self, host, port):  # Sobrecarga de metodos
        self.sock.connect((host, port))

    def client(self, host, port, msg):
        sent = self.sock.send(msg)
        print "Sent\n"

    def run(self):
        lista = []
        salir = ""
              

        for nodo in listaIPValidas:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                host = nodo
                port = 8999
            except EOFError:
                print "Error"
                return 1

            #print "Connecting\n"
            self.connect(host, port)
            lista.append(self.sock)
            print nodo  + "Connected\n"
            listaIPValidas.remove(nodo)

        while 1:
            print "Waiting for message\n"
            msg = raw_input('>>')
            if msg == 'exit':
                break
            if msg == '':
                continue
            print "Sending\n"

            for sock in lista:
                sock.send(msg)
        return (1)


if __name__ == '__main__':
    
    srv = Server()
    srv.daemon = True
    print "Starting server"
    srv.start()
    time.sleep(1)
    nod = GetNodes()
    nod.start()
    print "Starting client"
    cli = Client()
    print "Started successfully"
    cli.start()

