""" READ the data on the data bus

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512
"""

from machine import Pin
from busdata import BusData

data = BusData( [Pin(6),Pin(7),Pin(8),Pin(9),Pin(10),Pin(11),Pin(12),Pin(13)] )
data.config( Pin.IN )

_val = data.value
print( "Get data 0x%02X  =  %s" % (_val,bin(_val)) )
