""" EEPROM Programmer DATA BUS controler.

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512
"""
from machine import Pin, mem32

__version__ = "0.0.1"
__repo__ = "https://github.com/mchobby/micropython-eeprom-27512"

SIO_BASE = 0xd0000000
GPIO_IN  = SIO_BASE + 0x004

class BusData:
	def __init__( self, pins ): # 8 data pins LSBF
		assert len(pins)==8, "Must have 8 bits!"
		self.bits = pins
		self.mode = None
		# configure as input
		self.config( Pin.IN )

	def config( self, mode ):
		assert mode in (Pin.IN, Pin.OUT ), "Only IN or OUT allowed"
		self.mode = mode
		for p in self.bits:
			if mode == Pin.OUT:
				p.init( mode, value=False )
			else:
				p.init( mode )

	@property
	def value( self ):
		assert self.mode == Pin.IN
		return (mem32[GPIO_IN]>>6) & 0xFF

	@value.setter
	def value( self, value ):
		assert self.mode == Pin.OUT
		for i in range( 8 ):
			self.bits[i].value( (value & (1<<i)) )
