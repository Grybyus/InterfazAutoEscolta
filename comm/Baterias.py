from .CamReceiver import CamReceiver

class Baterias(object):
	"""
	baterias:
		'CB2':{#conjunto de baterías 1
			SN:'12623'
			t_PCB : float
			t_Cell: float
			v_Cells:int[8] 
		}
	minVolt :
		{
			mV:int
			CMUNumber:int
			CellNumber:int
		}
	maxVolt :
		{
			mV:int
			CMUNumber:int
			CellNumber:int
		}
	minTemp :
		{
			mV:flotat
			CMUNumber:int
		}
	maxTemp :
		{
			mV:float
			CMUNumber:int
		}
	"""
	@property
	def SOC_ah(self): return self._SOC_ah
	@SOC_ah.setter
	def SOC_ah(self, value):
		if(self._SOC_ah!=value):
			self._SOC_ah = value
			self.notifyAll()

	@property
	def SOC_p(self): return self._SOC_p
	@SOC_p.setter
	def SOC_p(self, value):
		if(self._SOC_p!=value):
			self._SOC_p = value
			self.notifyAll()


	def __init__(self):
		self.CB1 = {'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
		self.CB2 = {'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
		self.CB3 = {'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
		self.CB4 = {'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
		self.CB5 = {'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}
		self.CB6 = {'SN':'','t_PCB':0.0,'t_Cell':0.0,'v_Cells':[0,0,0,0,0,0,0,0]}

		self._SOC_ah = 0.0
		self._SOC_p = 0.0

		self.minVolt = { 'mV': 0.0, 'CMUNumber':0,'CellNumber':0}
		self.maxVolt = { 'mV': 0.0, 'CMUNumber':0,'CellNumber':0}
		self.minTemp = { 'mT': 0.0, 'CMUNumber':0}
		self.maxTemp = { 'mT': 0.0, 'CMUNumber':0}

		#CAM bus
		#TODO: iniciar solo los datos que le interesen al piloto en modo piloto
		self.receiver = CamReceiver()
		#CB1
		self.receiver.addEventHandler(0x0601,self,self.crCB1T1EventHandler)
		self.receiver.addEventHandler(0x0602,self,self.crCB1T2EventHandler)
		self.receiver.addEventHandler(0x0603,self,self.crCB1T3EventHandler)
		#CB2
		self.receiver.addEventHandler(0x0604,self,self.crCB2T1EventHandler)
		self.receiver.addEventHandler(0x0605,self,self.crCB2T2EventHandler)
		self.receiver.addEventHandler(0x0606,self,self.crCB2T3EventHandler)
		#CB3
		self.receiver.addEventHandler(0x0607,self,self.crCB3T1EventHandler)
		self.receiver.addEventHandler(0x0608,self,self.crCB3T2EventHandler)
		self.receiver.addEventHandler(0x0609,self,self.crCB3T3EventHandler)
		#CB4
		self.receiver.addEventHandler(0x060A,self,self.crCB4T1EventHandler)
		self.receiver.addEventHandler(0x060B,self,self.crCB4T2EventHandler)
		self.receiver.addEventHandler(0x060C,self,self.crCB4T3EventHandler)
		#CB5
		self.receiver.addEventHandler(0x060D,self,self.crCB5T1EventHandler)
		self.receiver.addEventHandler(0x060E,self,self.crCB5T2EventHandler)
		self.receiver.addEventHandler(0x060F,self,self.crCB5T3EventHandler)
		#CB6
		self.receiver.addEventHandler(0x0610,self,self.crCB6T1EventHandler)
		self.receiver.addEventHandler(0x0611,self,self.crCB6T2EventHandler)
		self.receiver.addEventHandler(0x0612,self,self.crCB6T3EventHandler)
		#SOC
		self.receiver.addEventHandler(0x06F4,self,self.crSOCEventHandler)
		#MaxMin
		self.receiver.addEventHandler(0x06F8,self,self.crMMVEventHandler)
		self.receiver.addEventHandler(0x06F9,self,self.crMMtEventHandler)

		self.observers = []

	def notifyAll(self):
		for handler in self.observers:
			try:
				handler(self)
			except AttributeError as ae:
				print("obs no es observer")

	def register(self,handler):
		self.observers.append(handler)

	def unregister(self,handler):
		self.observers.remove(handler)
	#CB1
	def crCB1T1EventHandler(self,obj,datos):
		#errores,flags TODO: revisar documentacion
		bnot = False
		if self.CB1['SN']=='':
			bnot = True
			self.CB1['SN']=str(datos[7])
		if self.CB1['t_PCB']!=datos[5]:
			bnot = True
			self.CB1['t_PCB']=float(datos[5])/10.0
		if self.CB1['t_Cell']!=datos[6]:
			bnot = True
			self.CB1['t_Cell']=float(datos[6])/10.0
		if bnot:
			self.notifyAll()

	def crCB1T2EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB1['v_Cells'][i]!=datos[3+i]:
				bnot = True
				self.CB1['v_Cells'][i] = datos[3+i]
		if bnot:
			self.notifyAll()

	def crCB1T3EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB1['v_Cells'][4+i]!=datos[3+i]:
				bnot = True
				self.CB1['v_Cells'][4+i] = datos[3+i]
		if bnot:
			self.notifyAll()

	#CB2
	def crCB2T1EventHandler(self,obj,datos):
		#errores,flags TODO: revisar documentacion
		bnot = False
		if self.CB2['SN']=='':
			bnot = True
			self.CB2['SN']=str(datos[7])
		if self.CB2['t_PCB']!=datos[5]:
			bnot = True
			self.CB2['t_PCB']=float(datos[5])/10.0
		if self.CB2['t_Cell']!=datos[6]:
			bnot = True
			self.CB2['t_Cell']=float(datos[6])/10.0
		if bnot:
			self.notifyAll()

	def crCB2T2EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB2['v_Cells'][i]!=datos[3+i]:
				bnot = True
				self.CB2['v_Cells'][i] = datos[3+i]
		if bnot:
			self.notifyAll()

	def crCB2T3EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB2['v_Cells'][4+i]!=datos[3+i]:
				bnot = True
				self.CB2['v_Cells'][4+i] = datos[3+i]
		if bnot:
			self.notifyAll()

	#CB3
	def crCB3T1EventHandler(self,obj,datos):
		#errores,flags TODO: revisar documentacion
		bnot = False
		if self.CB3['SN']=='':
			bnot = True
			self.CB3['SN']=str(datos[7])
		if self.CB3['t_PCB']!=datos[5]:
			bnot = True
			self.CB3['t_PCB']=float(datos[5])/10.0
		if self.CB3['t_Cell']!=datos[6]:
			bnot = True
			self.CB3['t_Cell']=float(datos[6])/10.0
		if bnot:
			self.notifyAll()

	def crCB3T2EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB3['v_Cells'][i]!=datos[3+i]:
				bnot = True
				self.CB3['v_Cells'][i] = datos[3+i]
		if bnot:
			self.notifyAll()

	def crCB3T3EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB3['v_Cells'][4+i]!=datos[3+i]:
				bnot = True
				self.CB3['v_Cells'][4+i] = datos[3+i]
		if bnot:
			self.notifyAll()
	#CB4
	def crCB4T1EventHandler(self,obj,datos):
		#errores,flags TODO: revisar documentacion
		bnot = False
		if self.CB4['SN']=='':
			bnot = True
			self.CB4['SN']=str(datos[7])
		if self.CB4['t_PCB']!=datos[5]:
			bnot = True
			self.CB4['t_PCB']=float(datos[5])/10.0
		if self.CB4['t_Cell']!=datos[6]:
			bnot = True
			self.CB4['t_Cell']=float(datos[6])/10.0
		if bnot:
			self.notifyAll()

	def crCB4T2EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB4['v_Cells'][i]!=datos[3+i]:
				bnot = True
				self.CB4['v_Cells'][i] = datos[3+i]
		if bnot:
			self.notifyAll()

	def crCB4T3EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB4['v_Cells'][4+i]!=datos[3+i]:
				bnot = True
				self.CB4['v_Cells'][4+i] = datos[3+i]
		if bnot:
			self.notifyAll()
	#CB5
	def crCB5T1EventHandler(self,obj,datos):
		#errores,flags TODO: revisar documentacion
		bnot = False
		if self.CB5['SN']=='':
			bnot = True
			self.CB5['SN']=str(datos[7])
		if self.CB5['t_PCB']!=datos[5]:
			bnot = True
			self.CB5['t_PCB']=float(datos[5])/10.0
		if self.CB5['t_Cell']!=datos[6]:
			bnot = True
			self.CB5['t_Cell']=float(datos[6])/10.0
		if bnot:
			self.notifyAll()

	def crCB5T2EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB5['v_Cells'][i]!=datos[3+i]:
				bnot = True
				self.CB5['v_Cells'][i] = datos[3+i]
		if bnot:
			self.notifyAll()

	def crCB5T3EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB5['v_Cells'][4+i]!=datos[3+i]:
				bnot = True
				self.CB5['v_Cells'][4+i] = datos[3+i]
		if bnot:
			self.notifyAll()
	#CB6
	def crCB6T1EventHandler(self,obj,datos):
		#errores,flags TODO: revisar documentacion
		bnot = False
		if self.CB6['SN']=='':
			bnot = True
			self.CB6['SN']=str(datos[7])
		if self.CB6['t_PCB']!=datos[5]:
			bnot = True
			self.CB6['t_PCB']=float(datos[5])/10.0
		if self.CB6['t_Cell']!=datos[6]:
			bnot = True
			self.CB6['t_Cell']=float(datos[6])/10.0
		if bnot:
			self.notifyAll()

	def crCB6T2EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB6['v_Cells'][i]!=datos[3+i]:
				bnot = True
				self.CB6['v_Cells'][i] = datos[3+i]
		if bnot:
			self.notifyAll()

	def crCB6T3EventHandler(self,obj,datos):
		bnot = False
		for i in range(4):
			if self.CB6['v_Cells'][4+i]!=datos[3+i]:
				bnot = True
				self.CB6['v_Cells'][4+i] = datos[3+i]
		if bnot:
			self.notifyAll()
	#SOC
	def crSOCEventHandler(self,obj,datos):
		self.SOC_ah = datos[1]
		self.SOC_p = datos[2]
	#MaxMin	
	def crMMVEventHandler(self,obj,datos):
		bnot = False
		#min
		#if self.minVolt['mV'] != datos[17]:
		#	bnot = True
		self.minVolt['mV'] = datos[17]
		if self.minVolt['CMUNumber'] != datos[27]:
			bnot = True
			self.minVolt['CMUNumber'] = datos[27]
		if self.minVolt['CellNumber'] != datos[28]:
			bnot = True
			self.minVolt['CellNumber'] = datos[28]
		#max
		if self.maxVolt['mV'] != datos[18]:
			bnot = True
			self.maxVolt['mV'] = datos[18]
		if self.maxVolt['CMUNumber'] != datos[29]:
			bnot = True
			self.maxVolt['CMUNumber'] = datos[29]
		if self.maxVolt['CellNumber'] != datos[30]:
			bnot = True
			self.maxVolt['CellNumber'] = datos[30]
		if bnot:
			self.notifyAll()
	#MaxMin	
	def crMMtEventHandler(self,obj,datos):
		bnot = False
		#min
		if self.minTemp['mT'] != datos[3]/10.0:
			bnot = True
			self.minTemp['mT'] = datos[3]/10.0
		if self.minTemp['CMUNumber'] != datos[27]:
			bnot = True
			self.minTemp['CMUNumber'] = datos[27]
		#max
		if self.maxTemp['mT'] != datos[4]/10.0:
			bnot = True
			self.maxTemp['mT'] = datos[4]/10.0
		if self.maxTemp['CMUNumber'] != datos[29]:
			bnot = True
			self.maxTemp['CMUNumber'] = datos[29]
		self.notifyAll()

		