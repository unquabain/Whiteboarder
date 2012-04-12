from numpy import *
from numpy.linalg import *

class Angle(float):
	pass

class Degree(Angle):
	def to_degrees(self):
		return self

class Radian(Angle):
	def to_degrees(self):
		return Degree(( self / math.pi ) * 180.)
	def to_radians(self):
		return self
	def sin(self):
		return sin(self)
	def cos(self):
		return cos(self)
	def tan(self):
		return tan(self)

	@classmethod
	def arcsin(cls, num, denom=1.0):
		return Radian(arcsin(num/denom))
	@classmethod
	def arccos(cls, num, denom=1.0):
		return Radian(arccos(num/denom))
	@classmethod
	def arctan(cls, num, denom=1.0):
		return Radian(arctan(num/denom))

class Degree(Angle):
	def to_radians(self):
		return Radian(( self / 180. ) * math.pi )
	def sin(self):
		return self.to_radians().sin()
	def cos(self):
		return self.to_radians().cos()
	def tan(self):
		return self.to_radians().tan()

	@classmethod
	def arcsin(cls, num, denom=1.0):
		return Degree(arcsin(num/denom))
	@classmethod
	def arccos(cls, num, denom=1.0):
		return Degree(arccos(num/denom))
	@classmethod
	def arctan(cls, num, denom=1.0):
		return Degree(arctan(num/denom))


