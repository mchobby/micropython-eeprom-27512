""" Read 64 Kio EEPROM by using Shift Register - driver for MicroPython

	16 bits counter. Use write word to count from 0 to 65535.
	Write word respect the MSBF (higher bit to the left).

	Execution time is about 96 seconds for 64 Kio.

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512
"""

from machine import Pin, mem32
from busaddr import BusAddr
from busdata import BusData
import time

read_led = Pin( 2, Pin.OUT, False )
# Note that signal is inverted by a 2N7002
oe = Pin(17, Pin.OUT, False )
ce = Pin(16, Pin.OUT, False )
# Disable programming Mode (for sure)
a9_prog = Pin(14, Pin.OUT, False) # Set High for Prog mode (see datasheet)
oe_prog = Pin(15, Pin.OUT, False) # Set High for Prog mode (see datasheet)


data = BusData( [Pin(6),Pin(7),Pin(8),Pin(9),Pin(10),Pin(11),Pin(12),Pin(13)] )
addr = BusAddr( Pin(20), Pin(21), Pin(19), Pin(18)  )

data.config( Pin.IN ) # Read mode
oe.value( True ) # Activates EEPROM
ce.value( True ) # Only required when CE is wired)

start_addr = 0x0000
end_addr   = 0xFFFF

read_led.on()
_addr = start_addr # Current address
_s = ""
_l = [] # Formatted Hex representation of data (2 hex digit each)
_ascii = [] # Ascci representatino of the data
t1 = time.time()
while _addr <= end_addr:
	addr.write_word( _addr )
	if (_addr % 256)==0:
		read_led.toggle()
	if (_addr % 16)==0:
		# Eject line to output
		if len( _l )>0 :
			print( _s + " ".join( _l ) + " : "+"".join(_ascii)  )
		# Prepare the next line
		_s = "0x%04X : " % _addr
		_l.clear()
		_ascii.clear()

	_val = data.value
	_l.append( "%02X" % _val )
	_ascii.append( "%c" % _val if 32<=_val<=126 else "." )
	_addr += 1


# Eject last line if any
if len( _l )>0 :
	print( _s + " ".join( _l ) + " : "+"".join(_ascii) )

oe.value( False )
read_led.off()
t2 = time.time()
# print( t2-t1, "seconds" )
