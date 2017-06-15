from comm.SensorReceiver import SensorReceiver
from comm.udptools import UDPTools

class mpptObservable(object):
	"""docstring for mpptObserver"""

	def __init__(self):
		self.receiver=SensorReceiver()
		self.updated=False
		if not self.receiver.running:
			self.receiver.open()
		#estructura principal
		self.Vin       = 0.0
		self.Iin       = 0.0
		self.Vout      = 0.0
		self.bulr      = 0.0
		self.out       = 0.0
		self.noe       = 0.0
		self.undv      = 0.0
		self.t         = 0.0
		#estructura extra
		self.t1        = 0.0
		self.t2        = 0.0
		self.corriente = 0.0
		#observadores
		self.observers = []
		self.receiver.addEventHandler(UDPTools.MPPT_STRUCT,self,self.mpptUpdateHandler)
		self.receiver.addEventHandler(UDPTools.EXTRAMPPT_STRUCT,self,self.extraUpdateHandler)

	def mpptUpdateHandler(self,obj,datos):
		self.Vin       = datos[1]
		self.Iin       = datos[2]
		self.Vout      = datos[3]
		self.bulr      = datos[4]
		self.out       = datos[5]
		self.noe       = datos[6]
		self.undv      = datos[7]
		self.t         = datos[8]
		self.updated   = True
		self.notifyAll()

	def extraUpdateHandler(self,obj,datos):
		self.t1        = datos[1]
		self.t2        = datos[2]
		self.corriente = datos[3]
		self.updated   = True
		self.notifyAll()

	def register(self,handler):
		self.observers.append(handler)

	def notifyAll(self):
		for obs in self.observers:
			try:
				obs(self)
			except AttributeError as ae:
				print("obs no es observer")
if __name__ == '__main__':
	#prueba funcional
	def handler(mppt):
		print ("""----
Generales\tExtra
Vin  = {0:.3f}\tt1        = {8:.3f}
Iin  = {1:.3f}\tt2        = {9:.3f}
Vout = {2:.3f}\tcorriente = {10:.3f}
bulr = {3:.3f}\t
out  = {4:.3f}\t
noe  = {5:.3f}\t
undv = {6:.3f}\t
t    = {7:.3f}\t
----"""
				.format(mppt.Vin ,
						mppt.Iin ,
						mppt.Vout,
						mppt.bulr,
						mppt.out ,
						mppt.noe ,
						mppt.undv,
						mppt.t   ,
						mppt.t1  ,
						mppt.t2  ,
						mppt.corriente))
	mppt = mpptObservable()
	mppt.register(handler)
	input("presione cualquier tecla para continuar\n")