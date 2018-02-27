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
import re
import os

listaIPValidas = []
listaIPUso = []
lista_socket = []

class GetNodes(threading.Thread):

    def run(self):
        #Obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipLocal = str(s.getsockname()[0])
        print ipLocal
        s.close()

        #Obtener mascara de subnet
        try:
            iface = commands.getoutput('ls /sys/class/net | grep wl')
            subnetMask = str (IPAddress(socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', str(iface)))[20:24])).netmask_bits())
            pass
        except IOError as e:
            iface = commands.getoutput('ls /sys/class/net | grep ens')
            subnetMask = str (IPAddress(socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', str(iface)))[20:24])).netmask_bits())
            pass
        print subnetMask

        #Obtener lista de hosts de la subnet actual
        listaIPs = []
        for ip in IPNetwork(ipLocal + "/" + subnetMask):
            listaIPs.append('%s' % ip)

        #now connect to the web server on port 80
        # - the normal http port
        global listaIPValidas
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
                        listaIPUso.append(ip)                        
                    pass
                except:
                    #print ip, 'No esta disponible'
                    pass 
                pass
            time.sleep(5)
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
                    global cli 
                    cli= Client()                    
                    print "Started successfully"
                    cli.start()
                    
            else:

                try:
                    filedir = sock.recv(1024)#1. Recive nombre de archivo
                    if os.path.isfile(filedir):
                        sock.send("EXISTE " + str(os.path.getsize(filedir)))#1. Envia existencia
                        userResponse1 = sock.recv(1024)#2. Recibe S/E
                        if userResponse1 == 'S':
                            with open(filedir, 'rb') as f:
                                bytesToSend = f.read(1024)
                                sock.send(bytesToSend)#3. Envia Sincronizacion
                                while bytesToSend != "":
                                    bytesToSend = f.read(1024)
                                    sock.send(bytesToSend)#4. Envia Sincronizacion Total
                        elif userResponse1 == 'E':
                        	sock.recv(1024)#3.Recibe Confirmacion
                            os.system('rm ' + filedir)
                            sock.send(filedir, ' Eliminado!!')#3. Envia Eliminado

                    elif os.path.isdir(filedir):
                        sock.send("EXISTE " + str(os.path.getsize(filedir)))#1. Envia existencia
                        userResponse1 = sock.recv(1024)#2. Recibe S/E
                        if userResponse1 == 'S':
                            with os.mkdir(filedir) as f:
                                bytesToSend = f.read(1024)#3. Envia Sincronizacion
                                sock.send(bytesToSend)
                                while bytesToSend != "":
                                    bytesToSend = f.read(1024)
                                    sock.send(bytesToSend)#4. Envia Sincronizacion Total
                        elif userResponse1 == 'E':
                        	sock.recv(1024)#3.Recibe Confirmacion
                            os.system('rm ' + filedir)
                            sock.send(filedir, ' Eliminado!!')#3. Envia Eliminado

		    #else:
			#sock.send("ERROR")
                    #data = sock.recv(4096)
                    #if data:
                        #print "[" + str(sock.getpeername()) + "]" + " > " + data

                    else:
                        sock.send("ERROR")
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

        for nodo in listaIPUso:            
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
            print nodo  + " Connected\n"
            listaIPUso.remove(nodo)

        while 1:
            for sock in lista:
                filedir = raw_input("filename? -> ")
                if filedir != 'q':
                    sock.send(filedir)#1. Envia nombre de archivo
                    data = sock.recv(1024)#1. Recibe existencia
                    if data[:6] == 'EXISTE':
                        filesize = long(data[6:])
                        msg = raw_input("Desea Sincronizar, Eliminar? (S/E) -> ")
                        if msg == 'S':
                            sock.send(msg)#2. Envia S/E
                            message = raw_input("File Existe. " + str(filesize) + "Que necesita Archivo, Directorio? (A/D)? -> ")
                            if message == 'A':
                            	f = open(filedir, "wb")
                                data = sock.recv(1024)#2. Recibe Sincronizacion
                                totalRecv = len(data)
                                f.write(data)
                                while totalRecv < filesize:
                                    data = sock.recv(1024)#2. Recibe Sincronizacion Total
                                    totalRecv += len(data)
                                    f.write(data)
                                    print "{0:.2f}".format((totalRecv/float(filesize))*100) + "% Done"
                                print "Download Complete!"
                            elif message == 'D':
                                f = os.mkdir(filedir)
                                data = sock.recv(1024)#2. Recibe Sincronizacion
                                totalRecv = len(data)
                                f.write(data)
                                while totalRecv < filesize:
                                    data = sock.recv(1024)#2. Recibe Sincronizacion Total
                                    totalRecv += len(data)
                                    f.write(data)
                                    print "{0:.2f}".format((totalRecv/float(filesize))*100) + "% Done"
                                print "Download Complete!"
                        elif msg == 'E':
                            sock.send(msg)#2. Envia S/E
                            message = raw_input("Esta Seguro. " + str(filesize) + "SI/NO? (S/N)? -> ")
                            if message == 'S':
                               sock.send(message)
                               os.system('rm ' + filedir)
                               ServerMsg = sock.recv(1024)#3. Recibe Eliminado
                               print ServerMsg



        else:
            print "File no Existe!"

            #print "Waiting for message\n"
            #msg = raw_input('>>')
            #print msg
            #if msg == 'exit':
                #break
            #if msg == '':
                #continue
            #print "Sending\n"

            #for sock in lista:
                #sock.send(msg)
        return (1)


if __name__ == '__main__':
    
    srv = Server()
    #srv.daemon = True
    print "Starting server"
    srv.start()
    time.sleep(1)
    nod = GetNodes()
    nod.start()
    print "Starting client"
    #cli = Client()
    print "Started successfully"
    #cli.start()

