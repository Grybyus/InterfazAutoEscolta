from comm.Controlador import Controlador

class ControladorObserver(object):
	"""docstring for ControladorObserver"""
	def __init__(self):
		self.updated = True
		self.driver = Controlador()
		self.driver.register(self.updateHandler)

	def connect(self):
		self.driver.receiver.open()

	def updateHandler(self,obj):
		self.updated=True

	def getDriver(self):
		return self.driver