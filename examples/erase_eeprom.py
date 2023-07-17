""" Write 64 Kio EEPROM with 1 Kio sample data. - driver for MicroPython

	16 bits counter. Use write word to count from 0 to 65535.
	Write word respect the MSBF (higher bit to the left).

	Execution time is about ?? seconds for 64 Kio.

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512
"""

from machine import Pin
from busdata import BusData
from busaddr import BusAddr
import time

# Note that signal is inverted by a 2N7002
read_led = Pin( 2, Pin.OUT, False )
oe = Pin(17, Pin.OUT, False ) # not selected
ce = Pin(16, Pin.OUT, False ) # Note active
a9_prog = Pin(14, Pin.OUT, False) # Set High for Prog mode (see datasheet)
oe_prog = Pin(15, Pin.OUT, False) # Set High for Prog mode (see datasheet)


data = BusData( [Pin(6),Pin(7),Pin(8),Pin(9),Pin(10),Pin(11),Pin(12),Pin(13)] )
addr = BusAddr( Pin(20), Pin(21), Pin(19), Pin(18)  )

data.config( Pin.IN ) # Read mode
addr.write_word( 0x0000 ) # ensure A9 = Low

a9_prog.on() # Set 12V on A9 (Erase mode)
time.sleep_ms( 1 )

oe.value( False ) # Ensure OE is deactivated ()
oe_prog.on() # Set 12V on OE (programmation mode)

ce.on() # Pulse for 100ms to erase
time.sleep_ms( 100 )
ce.off()

# Disable Erase mode
oe_prog.off() # OE as Output Enable
a9_prog.off() # A9 set as address line

# Time for recover
time.sleep( 1 )

#  Configure for read mode
read_led.on()
data.config( Pin.IN )
oe.on()
ce.on()
start_addr = 0x0000
end_addr   = 0xFFFF

t1 = time.time()
_addr = start_addr # Current address
while _addr <= end_addr:
	addr.write_word( _addr )
	if (_addr % 256)==0:
		read_led.toggle()
	if (_addr % 1024)==0:
		print( "Check %04x to %04x" % (_addr, _addr+1024) )

	if data.value != 0xFF:
		raise Exception( "Erase Failure. Value @ %04x is no 0xFF (%02x readed) " % (_addr, data.value) )
	_addr += 1

# Disable read Mode
oe.off()
ce.off()
read_led.off()
t2 = time.time()
print( "All bytes at 0xFF :-)" )
print( t2-t1, "seconds" )
