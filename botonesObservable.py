from comm.SensorReceiver import SensorReceiver
from comm.udptools import UDPTools
import traceback

class botonesObservable(object):
	"""docstring for botonesObservable"""
	def __init__(self):
		self.receiver=SensorReceiver()
		self.updated=False
		if not self.receiver.running:
			self.receiver.open()
		#estructura principal
		self.mppt      = False#int 32 //flag
		self.pan1      = False
		self.pan2      = False
		self.pan3      = False
		self.lucesAl   = False# int 32 //flag
		self.lucesBa   = False
		self.lucesEm   = False
		self.fan       = 0#int 32 //[0-255]
		self.bateria   = False# int 32 //flag
		self.observers = []
		self.receiver.addEventHandler(UDPTools.BOTONES_STRUCT,self,self.btnesUpdateHandler)

	def btnesUpdateHandler(self,obj,datos):
		self.mppt      = datos[1]&(1<<0)!=0#int 32 //flag
		self.pan1      = datos[1]&(1<<1)!=0
		self.pan2      = datos[1]&(1<<2)!=0
		self.pan3      = datos[1]&(1<<3)!=0
		self.lucesAl   = datos[2]&(1<<0)!=0# int 32 //flag
		self.lucesBa   = datos[2]&(1<<1)!=0
		self.lucesEm   = datos[2]&(1<<2)!=0
		self.fan       = datos[3]#int 32 //[0-255]
		self.bateria   = datos[4]!=0# int 32 //flag
		self.updated   = True
		self.notifyAll()

	def register(self,handler):
		self.observers.append(handler)

	def notifyAll(self):
		for obs in self.observers:
			try:
				obs(self)
			except AttributeError as ae:
				traceback.print_exc()
				print("obs no es observer")

if __name__ == '__main__':
	#prueba funcional
	def handler(botones):
		print ("""----
MPPT     LUCES      Vent/bateria
{0}    B:{4}       {7}
{1}    A:{5}       {8}
{2}    E:{6}
{3}
----"""
				.format(botones.mppt,botones.pan1,botones.pan2,botones.pan3,botones.lucesAl,botones.lucesBa,botones.lucesEm,botones.fan,botones.bateria))
	botones = botonesObservable()
	botones.register(handler)
	input("presione cualquier tecla para continuar\n")