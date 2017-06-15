from comm.Motor import Motor

class MotorObserver(object):
	"""docstring for MotorObserver"""
	def __init__(self):
		self.updated = True
		self.Motor = Motor()
		self.Motor.register(self.updateHandler)

	def connect(self):
		self.Motor.receiver.open()

	def updateHandler(self,obj):
		self.updated=True

	def getMotor(self):
		return self.Motor