from comm.SensorReceiver import SensorReceiver
from comm.udptools import UDPTools
from datetime import datetime
import re

class gpsObservable(object):
	"""docstring for gpsObservable"""
	def __init__(self,rec):
		self.receiver = rec
		self.updated=False
		#if not self.receiver.running:
		#	self.receiver.open()
		#estructura gps
		self.lat        = 0.0 #latitud:float
		self.lon        = 0.0 #longitud:float
		self.alt        = 0.0 #altitud:float
		self.err        = 0 #error[metros]:int
		self.lastUpdate = datetime.today()#ultima vez actualizado:datetime
		#observadores
		self.observers = []
		self.receiver.addEventHandler(UDPTools.GPS_STRUCT,self,self.gpsUpdateHandler)

	def gpsUpdateHandler(self,obj,datos):
		self.lat         = datos.get('lat',0.0)
		self.lon         = datos.get('lon',0.0)
		self.alt         = datos.get('alt',0.0)
		self.err         = datos.get('err',0)
		self.lastUpdate  = datetime.fromtimestamp(datos.get('lastUpdate',1538544876))
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
		print ("----\nlat:{0},lon:{1}\nalt:{2},err:{3}[mts]\nlu:{4}\n----"
				.format(gps.lat,gps.lon,gps.alt,gps.err,gps.lastUpdate))
	gps = gpsObservable()
	gps.register(handler)
	input("presione cualquier tecla para continuar\n")
