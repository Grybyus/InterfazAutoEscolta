from .CamReceiver import CamReceiver

class Controlador(object):
	"""
		Clase que recive y filtra los datos de los cambios.
	 	Funciona como un observer
	"""
	@property
	def reverse(self): return self._reverse
	@reverse.setter
	def reverse(self, value):
		if(self._reverse!=value):
			self._reverse = value
			self.notifyAll()

	@property
	def neutral(self): return self._neutral
	@neutral.setter
	def neutral(self, value):
		if(self._neutral!=value):
			self._neutral = value
			self.notifyAll()

	@property
	def regen(self): return self._regen
	@regen.setter
	def regen(self, value):
		if(self._regen!=value):
			self._regen = value
			self.notifyAll()

	@property
	def drive(self): return self._drive
	@drive.setter
	def drive(self, value):
		if(self._drive!=value):
			self._drive = value
			self.notifyAll()

	@property
	def accesories(self): return self._accesories
	@accesories.setter
	def accesories(self, value):
		if(self._accesories!=value):
			self._accesories = value
			self.notifyAll()

	@property
	def run(self): return self._run
	@run.setter
	def run(self, value):
		if(self._run!=value):
			self._run = value
			self.notifyAll()

	@property
	def start(self): return self._start
	@start.setter
	def start(self, value):
		if(self._start!=value):
			self._start = value
			self.notifyAll()

	@property
	def brakes(self): return self._brakes
	@brakes.setter
	def brakes(self, value):
		if(self._brakes!=value):
			self._brakes = value
			self.notifyAll()

	@property
	def fueldoor(self): return self._fueldoor
	@fueldoor.setter
	def fueldoor(self, value):
		if(self._fueldoor!=value):
			self._fueldoor = value
			self.notifyAll()
	@property
	def spVelocity(self): return self._spVelocity
	@spVelocity.setter
	def spVelocity(self, value):
		if(self._spVelocity!=value):
			self._spVelocity = value
			self.notifyAll()
			
	@property
	def spCurrent(self): return self._spCurrent
	@spCurrent.setter
	def spCurrent(self, value):
		if(self._spCurrent!=value):
			self._spCurrent = value
			self.notifyAll()

	@property
	def spBusCurrent(self): return self._spBusCurrent
	@spBusCurrent.setter
	def spBusCurrent(self, value):
		if(self._spBusCurrent!=value):
			self._spBusCurrent = value
			self.notifyAll()

	

	def __init__(self):
		self._reverse = False
		self._neutral = False
		self._regen = False
		self._drive = False
		self._accesories = False
		self._run = False
		self._start = False
		self._brakes = False
		self._fueldoor = False
		self._spCurrent = 0.0
		self._spBusCurrent = 0.0
		self._spVelocity = 0.0 

		self.receiver = CamReceiver()
		#cambios
		self.receiver.addEventHandler(0x0505,self,self.crEventHandler)
		#corrientes y velocidad
		self.receiver.addEventHandler(0x0501,self,self.crCVEventHandler)
		self.receiver.addEventHandler(0x0502,self,self.crBCEventHandler)

		self.observers = []

	def __del__(self):
		self.receiver.removeEventHandler(0x0505,self,self.crEventHandler)

	def notifyAll(self):
		for obs in self.observers:
			try:
				obs(self)
			except AttributeError as ae:
				print("obs no es observer")

	def register(self,handler):
		self.observers.append(handler)

	def unregister(self,handler):
		self.observers.remove(handler)

	def crEventHandler(self,obj,datos):
		x = datos[7]
		obj.reverse = x&(1<<0)>0
		obj.neutral = x&(1<<1)>0
		obj.regen = x&(1<<2)>0
		obj.drive = x&(1<<3)>0
		obj.accesories = x&(1<<4)>0
		obj.run = x&(1<<5)>0
		obj.start = x&(1<<6)>0
		obj.brakes = x&(1<<7)>0
		obj.fueldoor = x&(1<<8)>0

	def crCVEventHandler(self,obj,datos):
		#current,velocity 501 
		self.spCurrent = datos[2]
		self.spVelocity = datos[1]

	def crBCEventHandler(self,obj,datos):
		self.spBusCurrent = datos[2]