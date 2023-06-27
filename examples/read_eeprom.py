""" 74hc595, Shift Register - driver for MicroPython

	16 bits counter. Use write word to count from 0 to 65535.
	Write word respect the MSBF (higher bit to the left).

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/esp8266-upy/tree/master/74hc595
"""

from machine import Pin, Signal
from sn74hc595 import ShiftReg
import time

# Note that signal is inverted by a 2N7002
oe = Pin(17, Pin.OUT, False )
ce = Pin(16, Pin.OUT, False )

class DataIO:
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
		_r = 0
		for i in range( 8 ):
			_r +=  (self.bits[i].value() * (1<<i))
		return _r

	@value.setter
	def value( self, value ):
		assert self.mode == Pin.OUT
		for i in range( 8 ):
			self.bits[i].value( (value & (1<<i)) )


data = DataIO( [Pin(6),Pin(7),Pin(8),Pin(9),Pin(10),Pin(11),Pin(12),Pin(13)] )
addr = ShiftReg( Pin(20), Pin(21), Pin(19), Pin(18)  )

data.config( Pin.IN ) # Read mode
oe.value( True ) # Activates EEPROM
ce.value( True ) # Only required when CE is wired)

start_addr = 0x0000
end_addr   = 0xFFFF

_addr = start_addr # Current address
_s = ""
_l = [] # Formatted Hex representation of data (2 hex digit each)
_ascii = [] # Ascci representatino of the data
while _addr <= end_addr:
	#oe.value( False )
	#time.sleep_ms(1)
	addr.write_word( _addr )
	if (_addr % 16)==0:
		# Eject line to output
		if len( _l )>0 :
			print( _s + " ".join( _l ) + " : "+"".join(_ascii)  )
		# Prepare the next line
		_s = "0x%04X : " % _addr
		_l.clear()
		_ascii.clear()
	#time.sleep_ms(1)
	#oe.value( True )
	#time.sleep_ms(100)
	_val = data.value
	_l.append( "%02X" % _val )
	_ascii.append( "%c" % _val if 32<=_val<=126 else "." )
	_addr += 1
	#addr.reset()
	#time.sleep_ms(1)


# Eject last line if any
if len( _l )>0 :
	print( _s + " ".join( _l ) + " : "+"".join(_ascii) )

# time.sleep(2)
# reg.reset( latch=True ) ## Apply the reset to output

oe.value( False )
