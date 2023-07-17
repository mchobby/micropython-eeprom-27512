""" Write 64 Kio EEPROM with 1 Kio sample data. - driver for MicroPython

	16 bits counter. Use write word to count from 0 to 65535.
	Write word respect the MSBF (higher bit to the left).

	Execution time is about ?? seconds for 64 Kio.

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512
"""

from machine import Pin
from busaddr import BusAddr
from busdata import BusData
import time

# Date sample of exactly 1 Kb
sample = [32, 32, 95, 95, 32, 32, 32, 32, 32, 32, 95, 32, 32, 32, 32, 13, 111, 39, 39, 41, 125, 95, 95, 95, 95, 47, 47, 32, 32, 32, 32, 13, 32, 96, 95, 47, 32, 32, 32, 32, 32, 32, 41, 32, 32, 32, 32, 13, 32, 40, 95, 40, 95, 47, 45, 40, 95, 47, 32, 32, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 44, 45, 46, 95, 95, 95, 44, 45, 46, 32, 32, 32, 32, 32, 32, 13, 92, 95, 47, 95, 32, 95, 92, 95, 47, 32, 32, 32, 32, 32, 32, 13, 32, 32, 41, 79, 95, 79, 40, 32, 32, 32, 32, 32, 32, 32, 32, 13, 32, 123, 32, 40, 95, 41, 32, 125, 32, 32, 32, 32, 32, 32, 32, 13, 32, 32, 96, 45, 94, 45, 39, 32, 32, 32, 32, 32, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 32, 32, 32, 124, 92, 124, 92, 32, 32, 32, 32, 32, 32, 32, 32, 13, 32, 32, 46, 46, 32, 32, 32, 32, 92, 32, 32, 32, 32, 32, 32, 13, 111, 45, 45, 32, 32, 32, 32, 32, 92, 92, 32, 32, 32, 32, 47, 13, 32, 118, 95, 95, 47, 47, 47, 92, 92, 92, 92, 95, 95, 47, 32, 13, 32, 32, 32, 123, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 32, 32, 32, 32, 123, 32, 32, 125, 32, 92, 92, 92, 123, 32, 32, 13, 32, 32, 32, 32, 60, 95, 124, 32, 32, 32, 32, 32, 32, 60, 95, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 65, 77, 79, 69, 66, 65, 115, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 33, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 124, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 46, 46, 46, 46, 46, 46, 46, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 42, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 122, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 111, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 79, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 111, 46, 111, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 45, 46, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 62, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 45, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 46, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 39, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 58, 95, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 58, 126, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 40, 46, 41, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 51, 61, 61, 61, 68, 95, 95, 46, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 95, 95, 95, 95, 95, 36, 46, 95, 95, 95, 95, 95, 32, 32, 32, 13, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 13, 32, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 32, 32, 32, 32, 13, 32, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 32, 32, 32, 32, 13, 95, 58, 58, 58, 58, 58, 58, 58, 58, 58, 58, 95, 32, 32, 32, 13, 101, 111, 102, 32, 49, 48, 50, 52, 32, 98, 121, 116, 101, 115, 32, 13 ]

read_led = Pin( 2, Pin.OUT, False )
# Note that signal is inverted by a 2N7002
oe = Pin(17, Pin.OUT, False ) # signal is High
oe.value( False )
ce = Pin(16, Pin.OUT, False ) # signal is High
ce.value( False )
a9_prog = Pin(14, Pin.OUT, False) # Set High for Prog mode (see datasheet)
a9_prog.value( False )
oe_prog = Pin(15, Pin.OUT, False) # Set High for Prog mode (see datasheet)
oe_prog.value( False )

data = BusData( [Pin(6),Pin(7),Pin(8),Pin(9),Pin(10),Pin(11),Pin(12),Pin(13)] )
data.config( Pin.IN ) # Read mode (for the moment)
addr = BusAddr( Pin(20), Pin(21), Pin(19), Pin(18)  )

# ==============================================================================
# Erasing EEPROM
# ==============================================================================

data.config( Pin.IN ) # Read mode
addr.write_word( 0x0000 ) # ensure A9 = Low

oe.value( False ) # Ensure OE is HIGH
oe_prog.on() # Set 12V on OE (programmation mode)
a9_prog.on() # Set 12V on A9 (Erase mode)
time.sleep_ms( 1 )

ce.on() # Set LOW for 100ms to 500ms to erase
time.sleep_ms( 500 )
ce.off() # Set HIGH

time.sleep_ms( 10 )

# Disable Erase mode
oe_prog.off() # OE as Output Enable
a9_prog.off() # A9 set as address line

# Time for recover
time.sleep_ms( 10 )

ce.on() # Set LOW

# ==============================================================================
# Check Erased
# ==============================================================================

#  Configure for read mode
read_led.on()
data.config( Pin.IN )
oe.on() # signal is Low
ce.on() # signal is Low
start_addr = 0x0000
end_addr   = 0xFFFF

t1 = time.time()
_addr = start_addr # Current address
while _addr <= end_addr:
	addr.write_word( _addr )
	if (_addr % 256)==0:
		read_led.toggle()
	if (_addr % 1024)==0:
		print( "Check %04x to %04x" % (_addr, _addr+1024-1) )

	if data.value != 0xFF:
		raise Exception( "Erase Failure. Value @ %04x is no 0xFF (%02x readed) " % (_addr, data.value) )
	_addr += 1

# Disable read Mode
oe.off() # Signal is High
ce.off() # Signal is High
read_led.off()
t2 = time.time()
print( "All bytes at 0xFF :-)" )
print( t2-t1, "seconds" )


# ==============================================================================
# Programming
# ==============================================================================

# Initialize Address
start_addr = 0x0000
end_addr   = 0xFFFF

# Initial condition
oe_prog.off() # Ensure not programming mode
data.config( Pin.IN ) # High Impedance
ce.off()  # signal is HIGH
oe.on() # Signal is LOW
addr.write_word( start_addr ) # Initialize Addr



t1 = time.time()
#  Activates programming mode on EEPROM
oe_prog.on() # Activate programming mode
time.sleep_ms(100)
# ce.off() alreadu high
data.config( Pin.OUT )


_addr = start_addr # Current address
sample_len = len( sample )
print( "Sample buffer: %i bytes" % sample_len )
# addr alreadu set addr.write_word( _addr )
while _addr <= end_addr:
	addr.write_word( _addr )
	if (_addr % sample_len)==0:
		print( "Programming from %4x to %4x" % (_addr, _addr+sample_len-1) )
	if (_addr % 16)==0 : # show some activities
		read_led.toggle()
	data.value = sample[_addr % sample_len]
	time.sleep_ms(1) # Gives the time to set the address
	ce.on() # Pulse LOW signal on ROM of 30uS
	ce.on()
	ce.on() # 20 µSec sharp
	ce.on() # 25 µSec
	ce.off() # signal is High
	_addr += 1

# Disable programming mode Mode
oe_prog.off()
# recover time
time.sleep_ms( 100 )
data.config( Pin.IN ) # High impedance
ce.on() # Set signal low
# oe is Low
read_led.off()

t2 = time.time()
print( t2-t1, "seconds" )

# ==============================================================================
# Check Programmed
# ==============================================================================

print( "Reread content" )
start_addr = 0x0000
end_addr   = 0xFFFF
_addr = start_addr # Current address
ce.on() # Signal is Low
oe.on() # Signal is Low
while _addr <= end_addr:
	addr.write_word( _addr )
	if( _addr % 256 )==0:
		read_led.toggle()
	_d = data.value
	_addr+=1
ce.off()
oe.off()
t2 = time.time()
print( t2-t1, "seconds" )
