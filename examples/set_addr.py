""" Set the BUS ADDRESS by using Shift Register - driver for MicroPython

	16 bits counter. Use write word to count from 0 to 65535.
	Write word respect the MSBF (higher bit to the left).

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512
"""

from machine import Pin
from busaddr import BusAddr

addr = BusAddr( Pin(20), Pin(21), Pin(19), Pin(18)  )

#_addr = 0b01010101_01010101
#_addr = 0b10101010_10101010
_addr = 0b11101111_10001110
addr.write_word( _addr )
print( "Set addr %04X  =  %s" % (_addr,bin(_addr)) )
