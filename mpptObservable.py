from comm.SensorReceiver import SensorReceiver
from comm.udptools import UDPTools

class mpptObservable(object):
	"""docstring for mpptObserver"""

	def __init__(self,rec):
		self.receiver = rec
		self.updated=False
		#if not self.receiver.running:
		#	self.receiver.open()
		#estructura principal
		self.paneles   =[{},{},{}]
		for i in range(3):
			self.paneles[i]["panelID"]   = i+1
			self.paneles[i]["Vin"]   = 0.0
			self.paneles[i]["Iin"]   = 0.0
			self.paneles[i]["Vout"]   = 0.0
			self.paneles[i]["bulr"]   = 0.0
			self.paneles[i]["out"]   = 0.0
			self.paneles[i]["noe"]   = 0.0
			self.paneles[i]["undv"]   = 0.0
			self.paneles[i]["t"]   = 0.0
		#estructura extra
		self.t1        = 0.0
		self.t2        = 0.0
		self.corriente = 0.0
		#observadores
		self.observers = []
		self.receiver.addEventHandler(UDPTools.MPPT_STRUCT,self,self.mpptUpdateHandler)
		self.receiver.addEventHandler(UDPTools.EXTRAMPPT_STRUCT,self,self.extraUpdateHandler)

	def mpptUpdateHandler(self,obj,datos):
		panelID                        = datos.get('idMPPT',0)
		self.paneles[panelID-1]["Vin"] = datos.get('Vin',0.0)
		self.paneles[panelID-1]["Iin"] = datos.get("Iin",0.0)
		self.paneles[panelID-1]["Vout"] = datos.get("Vout",0.0)
		self.paneles[panelID-1]["bulr"] = datos.get("bulr",0.0)
		self.paneles[panelID-1]["out"] = datos.get("out",0.0)
		self.paneles[panelID-1]["noe"] = datos.get("noe",0.0)
		self.paneles[panelID-1]["undv"] = datos.get("undv",0.0)
		self.paneles[panelID-1]["t"] = datos.get("t",0.0)
		self.updated               = True
		self.notifyAll()

	def extraUpdateHandler(self,obj,datos):
		self.t1        = datos.get('t1')
		self.t2        = datos.get('t2')
		self.corriente = datos.get('corriente')
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