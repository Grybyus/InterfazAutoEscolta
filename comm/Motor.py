from .CamReceiver import CamReceiver

class Motor(object):
	#401 
	@property
	def errores(self): return self._errores
	@errores.setter
	def errores(self, value):
		if(self._errores!=value):
			self._errores = value
			self.notifyAll()
	@property
	def flags(self): return self._flags
	@flags.setter
	def flags(self, value):
		if(self._flags!=value):
			self._flags = value
			self.notifyAll()
	@property
	def motorActivo(self): return self._motorActivo
	@motorActivo.setter
	def motorActivo(self, value):
		if(self._motorActivo!=value):
			self._motorActivo = value
			self.notifyAll()
	#402
	@property
	def current(self): return self._current
	@current.setter
	def current(self, value):
		if(self._current!=value):
			self._current = value
			self.notifyAll()
	@property
	def voltage(self): return self._voltage
	@voltage.setter
	def voltage(self, value):
		if(self._voltage!=value):
			self._voltage = value
			self.notifyAll()
	#403
	@property
	def velocidad(self): return self._velocidad
	@velocidad.setter
	def velocidad(self, value):
		if(self._velocidad!=value):
			self._velocidad = value
			self.notifyAll()
	@property
	def RPM(self): return self._RPM
	@RPM.setter
	def RPM(self, value):
		if(self._RPM!=value):
			self._RPM = value
			self.notifyAll()
	#404
	@property
	def phaseC(self): return self._phaseC
	@phaseC.setter
	def phaseC(self, value):
		if(self._phaseC!=value):
			self._phaseC = value
			self.notifyAll()
	@property
	def phaseB(self): return self._phaseB
	@phaseB.setter
	def phaseB(self, value):
		if(self._phaseB!=value):
			self._phaseB = value
			self.notifyAll()
	#408,409 voltages
	@property
	def voltage_1(self): return self._voltage_1
	@voltage_1.setter
	def voltage_1(self, value):
		if(self._voltage_1!=value):
			self._voltage_1 = value
			self.notifyAll()
	@property
	def voltage_2(self): return self._voltage_2
	@voltage_2.setter
	def voltage_2(self, value):
		if(self._voltage_2!=value):
			self._voltage_2 = value
			self.notifyAll()
	@property
	def voltage_3(self): return self._voltage_3
	@voltage_3.setter
	def voltage_3(self, value):
		if(self._voltage_3!=value):
			self._voltage_3 = value
			self.notifyAll()
	@property
	def voltage_4(self): return self._voltage_4
	@voltage_4.setter
	def voltage_4(self, value):
		if(self._voltage_4!=value):
			self._voltage_4 = value
			self.notifyAll()
	#40b
	@property
	def t_motor(self): return self._t_motor
	@t_motor.setter
	def t_motor(self, value):
		if(self._t_motor!=value):
			self._t_motor = value
			self.notifyAll()
	#40c disipador?
	@property
	def t_DSP(self): return self._t_DSP
	@t_DSP.setter
	def t_DSP(self, value):
		if(self._t_DSP!=value):
			self._t_DSP = value
			self.notifyAll()
	#40E
	@property
	def odometro(self): return self._odometro
	@odometro.setter
	def odometro(self, value):
		if(self._odometro!=value):
			self._odometro = value
			self.notifyAll()
	@property
	def ah(self): return self._ah
	@ah.setter
	def ah(self, value):
		if(self._ah!=value):
			self._ah = value
			self.notifyAll()


	"""docstring for Motor"""
	def __init__(self):
		self._errores = 0
		self._flags = 0
		self._motorActivo = 0

		self._current = 0.0
		self._voltage = 0.0
		self._velocidad = 0.0
		self._RPM = 0.0
		self._phaseC = 0.0
		self._phaseB = 0.0
		self._voltage_1 = 0.0
		self._voltage_2 = 0.0
		self._voltage_3 = 0.0
		self._voltage_4 = 0.0
		self._t_motor = 0.0
		self._t_DSP = 0.0
		self._odometro = 0.0
		self._ah = 0.0
		#CAM bus
		self.receiver = CamReceiver()
		self.receiver.addEventHandler(0x0401,self,self.cr401EventHandler)
		self.receiver.addEventHandler(0x0402,self,self.cr402EventHandler)
		self.receiver.addEventHandler(0x0403,self,self.cr403EventHandler)
		self.receiver.addEventHandler(0x0404,self,self.cr404EventHandler)
		self.receiver.addEventHandler(0x0408,self,self.cr408EventHandler)
		self.receiver.addEventHandler(0x0409,self,self.cr409EventHandler)
		self.receiver.addEventHandler(0x040B,self,self.cr411EventHandler)
		self.receiver.addEventHandler(0x040C,self,self.cr412EventHandler)
		self.receiver.addEventHandler(0x040E,self,self.cr414EventHandler)
		self.observers = []

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

	def cr401EventHandler(self,obj,datos):
		#errores,flags TODO: verificar
		obj.errores = datos[18]
		obj.flags = datos[17]
		obj.motorActivo = datos[19]#puede que sean tambien como un flag XOR

	def cr402EventHandler(self,obj,datos):
		#current voltage
		obj.current=datos[2]
		obj.voltage=datos[1]


	def cr403EventHandler(self,obj,datos):
		#velocidad rpm
		obj.velocidad=datos[2]*3.6
		obj.RPM=datos[1]

	def cr404EventHandler(self,obj,datos):
		#phaseC phaseB
		obj.phaseC=datos[2]
		obj.phaseB=datos[1]

	def cr408EventHandler(self,obj,datos):
		#voltages 1 2
		obj.voltage_1=datos[2]
		obj.voltage_2=datos[1]

	def cr409EventHandler(self,obj,datos):
		#voltages 3 4
		obj.voltage_3=datos[2]
		obj.voltage_4=datos[1]

	def cr411EventHandler(self,obj,datos):
		#t_motor TODO: ver porque no aparecen en el simulador
		#print(datos)
		obj.t_motor=datos[1]

	def cr412EventHandler(self,obj,datos):
		#t_DSP TODO: ver porque no aparecen en el simulador
		obj.t_DSP=datos[1]

	def cr414EventHandler(self,obj,datos):
		#odometro ah
		obj.odometro=datos[1]
		obj.ah=datos[2]
	def getErrorMSG(self):
		errores=[]

		if (self.errores&1)>0:
			errores.append((0,'Hardware over current',))
		if (self.errores&1<<1)>0:
			errores.append((1,'Software over current',))
		if (self.errores&1<<2)>0:
			errores.append((2,'DC Bus over voltage',))
		if (self.errores&1<<3)>0:
			errores.append((3,'Bad motor position hall sequence',))
		if (self.errores&1<<4)>0:
			errores.append((4,'Watchdog caused last reset',))
		if (self.errores&1<<5)>0:
			errores.append((5,'Config read error (some values may be reset to defaults)',))
		if (self.errores&1<<6)>0:
			errores.append((6,'A 15V rail under voltage lock out occurred',))

		return errores

	def getFlagsMSG(self):
		flags=[]
		if (self.flags&1)>0:
			flags.append((0,'Bridge PWM',))
		if (self.flags&1<<1)>0:
			flags.append((1,'Motor Current',))
		if (self.flags&1<<2)>0:
			flags.append((2,'Velocity',))
		if (self.flags&1<<3)>0:
			flags.append((3,'Bus Current',))
		if (self.flags&1<<4)>0:
			flags.append((4,'Bus Voltage Upper Limit',))
		if (self.flags&1<<5)>0:
			flags.append((5,'Bus Voltage Lower Limit',))
		if (self.flags&1<<6)>0:
			flags.append((6,'Heatsink Temperature',))
		return flags

		
