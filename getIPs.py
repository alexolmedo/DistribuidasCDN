import socket
import fcntl
import struct
from netaddr import IPAddress, IPNetwork

#Obtener IP local
iface = "wlp3s0"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ipLocal = str(s.getsockname()[0])
print ipLocal
s.close()

#Obtener mascara de subnet
subnetMask = str (IPAddress(socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), 35099, struct.pack('256s', iface))[20:24])).netmask_bits())
print subnetMask

#Obtener lista de hosts de la subnet actual
for ip in IPNetwork(ipLocal + "/" + subnetMask):
    print '%s' % ip

