from scapy.all import *
import netifaces

class Connection(object):

    def __init__(self):
        self.mac = netifaces.ifaddresses('wlp3s0')[netifaces.AF_LINK][0]["addr"]
        self.ip = netifaces.ifaddresses('wlp3s0')[2][0]['addr']

    def connect(self):
        # debe ser ejecutado con sudo
        # sniff(count=100)
        # a=_
        # a.nsummary()
        # a[2].command()
        # packet = eval(a[2].command())

        # copia del paquete capturado con lo de arriba
        packet = eval(
            'Ether(src=\'e8:b1:fc:32:29:66\', dst=\'01:00:5e:00:00:16\', type=2048)/IP(tos=192, dst=\'224.0.0.22\', src=\'192.168.0.66\', ttl=1, version=4, proto=2, frag=0, id=0, len=40, ihl=6, options=[IPOption_Router_Alert(length=4, option=20, copy_flag=1, alert=0, optclass=0)], flags=2, chksum=17086)/Raw(load=b\'"\\x00\\xad\\xc2\\x00\\x00\\x00\\x01\\x04\\x00\\x00\\x00\\xef\\xff<<\')')

        packet[0].src = self.mac
        packet[1].src = self.ip

        # Esto es en caso de que el pauqete se pierda
        sendp(packet)
        sendp(packet)

    def disconnect(self):
        # copia del paquete capturado con lo de arriba
        packet = eval(
            'Ether(dst=\'01:00:5e:00:00:16\', type=2048, src=\'e8:b1:fc:32:29:22\')/IP(dst=\'224.0.0.22\', ttl=1, flags=2, proto=2, version=4, ihl=6, id=0, src=\'192.168.0.147\', chksum=17086, options=[IPOption_Router_Alert(option=20, alert=0, optclass=0, copy_flag=1, length=4)], len=40, tos=192, frag=0)/Raw(load=b\'"\\x00\\xae\\xc2\\x00\\x00\\x00\\x01\\x03\\x00\\x00\\x00\\xef\\xff<<\')')

        packet[0].src = self.mac
        packet[1].src = self.ip

        # Esto es en caso de que el pauqete se pierda
        sendp(packet)
        sendp(packet)