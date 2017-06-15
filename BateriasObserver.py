from comm.Baterias import Baterias

class BateriasObserver(object):
	"""docstring for BateriasObserver"""
	def __init__(self):
		self.updated = True
		self.Battery = Baterias()
		self.Battery.register(self.updateHandler)

	def connect(self):
		self.Battery.receiver.open()

	def updateHandler(self,obj):
		self.updated=True

	def getBattery(self):
		return self.Battery