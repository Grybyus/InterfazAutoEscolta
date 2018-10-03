import sys
import _thread
import time
from .udptools import UDPTools
import traceback



def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if 'instances' not in globals():
        globals()['instances'] = {}
    if class_ not in globals()['instances']:
        globals()['instances'][class_] = class_(*args, **kwargs)
    return globals()['instances'][class_]
  return getinstance

#@singleton
class SensorReceiver(object):
	"""docstring for SensorReceiver"""
	receivers = {}

	@classmethod
	def getinstance(cls):
		return globals().get('SingletonReceiver',cls())

	def __init__(self):
		self.eventHandlers = {}
		self.running = False
		self.Escuchando = False

	def thread_lisent(self,tname,delay=0):
		self.Escuchando = True
		self.running=True
		while self.Escuchando:
			if(delay>0):
				time.sleep(delay)

			dato = UDPTools.Receive()

			if(str(dato.get("ctx",0)) in self.eventHandlers):
				for h,o in self.eventHandlers[str(dato.get("ctx",0))]:
					try:
						h(o,dato)
					except Exception as ez:
						traceback.print_exc()
						print(ez)

						print("La funcion no es un callback")
		self.running=False
	def open(self):
		if(not self.running):
			try:
				self.thread = _thread.start_new_thread( self.thread_lisent, ("Thread-1", 1, ) )
			except Exception as e:
				print(e)
				print ("Error: unable to start thread")
		else:
			print ("thread ya funcionando")

	def close(self):
		self.Escuchando=False

	def addEventHandler(self,hexID,obj,handler):
		if(str(hexID) in self.eventHandlers):
			self.eventHandlers[str(hexID)].append((handler,obj,))

		else:
			self.eventHandlers[str(hexID)]=[(handler,obj,)]
			#print(self.eventHandlers)

	def removeEventHandler(self,hexID,obj,handler):
		try:
			self.eventHandlers[str(hexID)].remove((handler,obj,))
		except:
			print("Evento no estaba registrado")

if __name__ == '__main__':
	def handler(o,d):
		print(d) 
	sr = SensorReceiver()
	sr.addEventHandler(UDPTools.GPS_STRUCT,sr,handler)
	sr.open()
	input("iniciando, presione cualquier tecla para terminar")
