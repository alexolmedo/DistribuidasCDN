import socket
import fcntl
import struct
from netaddr import IPAddress, IPNetwork
import signal
import commands

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

#print listaIPs


#now connect to the web server on port 80
# - the normal http port
for ip in listaIPs:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.01)
        s.connect((ip, 8999))
        print ip, 'Se conecto exitosamente'
        pass
    except :
        #print ip, 'No esta disponible'
        pass
    


