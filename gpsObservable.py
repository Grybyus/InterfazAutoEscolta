from comm.SensorReceiver import SensorReceiver
from comm.udptools import UDPTools
from datetime import datetime
import re

class gpsObservable(object):
	"""docstring for gpsObservable"""
	def __init__(self):
		self.receiver=SensorReceiver()
		self.updated=False
		if not self.receiver.running:
			self.receiver.open()
		#estructura gps
		self.lat        = 0.0 #latitud:float
		self.lon        = 0.0 #longitud:float
		self.alt        = 0.0 #altitud:float
		self.err        = 0 #error[metros]:int
		self.lastUpdate = datetime.fromtimestamp(0.0)#ultima vez actualizado:datetime
		self.heading    = 0.0 #grados de inclinacion respecto de la direccion[grados]:float
		#observadores
		self.observers = []
		self.receiver.addEventHandler(UDPTools.GPS_STRUCT,self,self.gpsUpdateHandler)

	def gpsUpdateHandler(self,obj,datos):
		self.lat         = datos[1]
		self.lon         = datos[2]
		self.alt         = datos[3]
		self.err         = datos[4]
		self.lastUpdate  = datetime.fromtimestamp(datos[5])
		self.heading     = datos[6]
		self.updated     = True
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
	def handler(gps):
		print ("----\nlat:{0},lon:{1}\nalt:{2},err:{3}[mts]\nlu:{4}\n{5}º\n----"
				.format(gps.lat,gps.lon,gps.alt,gps.err,gps.lastUpdate,gps.heading))
	gps = gpsObservable()
	gps.register(handler)
	input("presione cualquier tecla para continuar\n")