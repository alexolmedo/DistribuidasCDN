#! /usr/bin/env python

import socket
import sys
import time
import threading
import select

lista_socket = []


class Server(threading.Thread):
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Server started successfully\n"
        hostname = ''
        port = 7779
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
        while (salir != "si"):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                host = raw_input("Enter the hostname\n>>")
                port = int(raw_input("Enter the port\n>>"))
            except EOFError:
                print "Error"
                return 1

            print "Connecting\n"
            self.connect(host, port)
            lista.append(self.sock)
            print "Connected\n"
            salir = raw_input("Quiere salir si, no\n>>")

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
    print "Starting client"
    cli = Client()
    print "Started successfully"
    cli.start()    