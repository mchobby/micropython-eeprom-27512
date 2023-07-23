""" EEProm Programmer script will receive command through the USB-Serial
    and applies it to the EEPROM.

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/micropython-eeprom-27512

"""
__version__ = "0.0.1"
__repo__ = "https://github.com/mchobby/micropython-eeprom-27512"

from machine import Pin, mem32
from binascii import hexlify,unhexlify
from busaddr import BusAddr
from busdata import BusData
import time
import sys

SIO_BASE = 0xd0000000
GPIO_IN  = SIO_BASE + 0x004

class EProgrammer:
	def __init__( self ):
		self.read_led = Pin( 2, Pin.OUT, value=False )
		# Note that signal is inverted by a 2N7002
		self.oe = Pin(17, Pin.OUT, value=False ) # signal is High
		self.ce = Pin(16, Pin.OUT, value=False ) # signal is High
		self.a9_prog = Pin(14, Pin.OUT, value=False) # Set High for Prog mode (see datasheet)
		self.oe_prog = Pin(15, Pin.OUT, value=False) # Set High for Prog mode (see datasheet)

		self.data = BusData( [Pin(6),Pin(7),Pin(8),Pin(9),Pin(10),Pin(11),Pin(12),Pin(13)] )
		self.data.config( Pin.IN ) # Read mode (for the moment)
		self.addr = BusAddr( Pin(20), Pin(21), Pin(19), Pin(18)  )

	def crc8_itu(self, msg):
		crc = 0
		for byte in msg:
			crc ^= byte
			for _ in range(8):
				crc = (crc << 1) ^ 7 if crc & 0x80 else crc << 1
			crc &= 0xff
		return crc ^ 0x55


	def reset( self ):
		""" Reset the programmer """
		self.oe.value( False )
		self.ce.value( False )
		self.a9_prog.value( False )
		self.oe_prog.value( False )
		self.data.config( Pin.IN ) # Read mode (for the moment)
		self.addr.write_word( 0x0000 ) # ensure A9 = Low

	def erase( self ):
		""" Erase the EEPROM chip """
		self.data.config( Pin.IN ) # Read mode
		self.addr.write_word( 0x0000 ) # ensure A9 = Low

		self.oe.value( False ) # Ensure OE is HIGH
		self.oe_prog.on() # Set 12V on OE (programmation mode)
		self.a9_prog.on() # Set 12V on A9 (Erase mode)
		time.sleep_ms( 1 )

		self.ce.on() # Set LOW for 100ms to 500ms to erase
		time.sleep_ms( 500 )
		self.ce.off() # Set HIGH
		time.sleep_ms( 10 )

		# Disable Erase mode
		self.oe_prog.off() # OE as Output Enable
		self.a9_prog.off() # A9 set as address line
		# Time for recover
		time.sleep_ms( 10 )

		self.ce.on() # Set LOW

	def check_erased( self, start_addr, end_addr ):
		""" Check that all bytes from start_addr to end_addr(included) are 0xFF.
		    Will raise exception in case of issue """
		assert start_addr < end_addr
		#  Configure for read mode
		self.read_led.on()
		self.data.config( Pin.IN )
		self.oe.on() # signal is Low
		self.ce.on() # signal is Low
		#start_addr = 0x0000
		#end_addr   = 0xFFFF

		t1 = time.time()
		_addr = start_addr # Current address
		while _addr <= end_addr:
			self.addr.write_word( _addr )
			if (_addr % 256)==0:
				self.read_led.toggle()
			if (_addr % 1024)==0:
				print( "Check 0x%04x to 0x%04x" % (_addr, _addr+1024-1) )

			if self.data.value != 0xFF:
				raise Exception( "Check erasure failed. Value @ 0x%04x is 0x%02x (should be 0xFF)" % (_addr, self.data.value) )
			_addr += 1

		# Disable read Mode
		self.oe.off() # Signal is High
		self.ce.off() # Signal is High
		self.read_led.off()
		t2 = time.time()
		print( "All bytes at 0xFF :-)" )
		print( t2-t1, "seconds" )

	def read_text( self, start_addr, end_addr ):
		""" Read and return the data in a human friendly format like this
				0x2850 : 2C 2D 2E 5F 5F 5F 2C 2D 2E 20 20 20 20 20 20 0D : ,-.___,-.      .
				0x2860 : 5C 5F 2F 5F 20 5F 5C 5F 2F 20 20 20 20 20 20 0D : \_/_ _\_/      .
				0x2870 : 20 20 29 4F 5F 4F 28 20 20 20 20 20 20 20 20 0D :   )O_O(        .
				0x2880 : 20 7B 20 28 5F 29 20 7D 20 20 20 20 20 20 20 0D :  { (_) }       .
				0x2890 : 20 20 60 2D 5E 2D 27 20 20 20 20 20 20 20 20 0D :   `-^-'        .
 		"""
		self.data.config( Pin.IN ) # Read mode
		self.oe.value( True ) # Activates EEPROM
		self.ce.value( True ) # Only required when CE is wired)

		self.read_led.on()
		_addr = start_addr # Current address
		_s = ""
		_l = [] # Formatted Hex representation of data (2 hex digit each)
		_ascii = [] # Ascci representatino of the data
		t1 = time.time()
		while _addr <= end_addr:
			self.addr.write_word( _addr )
			if (_addr % 256)==0:
				self.read_led.toggle()
			if (_addr % 16)==0:
				# Eject line to output
				if len( _l )>0 :
					print( _s + " ".join( _l ) + " : "+"".join(_ascii)  )
				# Prepare the next line
				_s = "0x%04X : " % _addr
				_l.clear()
				_ascii.clear()

			_val = self.data.value
			_l.append( "%02X" % _val )
			_ascii.append( "%c" % _val if 32<=_val<=126 else "." )
			_addr += 1


		# Eject last line if any
		if len( _l )>0 :
			print( _s + " ".join( _l ) + " : "+"".join(_ascii) )

		self.oe.value( False )
		self.read_led.off()
		t2 = time.time()
		print( "read time %s sec" % (t2-t1))
		self.reset()


	def read_fast( self, start_addr, end_addr ):
		""" fast reading and returns binary based format as line of 16 bytes
		       under hexa format.
			Each line starting with address (2 bytes), 16 bytes and CRC8 on the line
			So a total of 19 bytes per line.

			f0605c5f2f5f205f5c5f2f2020202020200d12
			fde05f5f5f5f5f2e7a5f5f5f5f5f2020200d9e
			fdf02020202020202020202020202020200d5d
			fe005f5f5f5f5f5f5f5f5f5f5f5f2020200d83
			fe102020202020202020202020202020200d78
		"""
		arr = bytearray(19) # two first bytes is the address
		mv = memoryview( arr )

		self.data.config( Pin.IN ) # Read mode
		self.oe.value( True ) # Activates EEPROM
		self.ce.value( True ) # Only required when CE is wired)

		self.read_led.on()
		_addr = start_addr
		while _addr <= end_addr+1: # +1 ensure that last line is ejected to serial
			self.addr.write_word( _addr )
			if (_addr % 256)==0:
				self.read_led.toggle()
			if (_addr % 16)==0:
				# Calculate the CRC8 on the current data then
				#    eject the current line
				arr[18] = self.crc8_itu( mv[:18] ) # CRC8
				if _addr > start_addr:
					print( hexlify(arr).decode('UTF8') )
				# prepare next line
				arr[0] = _addr >> 8
				arr[1] = _addr & 0xFF
				arr[18] = 0x00 # CRC8

			# Using bytearray for storage
			arr[(_addr % 16) +2 ] = (mem32[GPIO_IN]>>6) & 0xFF

			#_l.append( "%02X" % _val )
			#_ascii.append( "%c" % _val if 32<=_val<=126 else "." )
			_addr += 1

		self.oe.value( False )
		self.read_led.off()
		self.reset()

	def upload( self, start_addr, end_addr ):
		""" Start upload data to EEPROM from start_addr until the end_addr """
		_addr = eval( start_addr )
		_end_addr = eval( end_addr )
		#print( "upload from _addr %s" % _addr )
		#print( 'to %s' % _end_addr )
		self.read_led.on()

		# Initial condition
		self.oe_prog.off() # Ensure not programming mode
		self.data.config( Pin.IN ) # High Impedance
		self.ce.off()  # signal is HIGH
		self.oe.on() # Signal is LOW
		self.addr.write_word( _addr ) # Initialize Addr

		t1 = time.time()
		#  Activates programming mode on EEPROM
		self.oe_prog.on() # Activate programming mode
		time.sleep_ms(100)
		# ce.off() alreadu high
		self.data.config( Pin.OUT )
		try:
			while _addr < _end_addr:
				# Write send "Next hexa packet"
				self.read_led.toggle()
				sys.stdout.write( "=" )
				s = sys.stdin.readline() # time out of 1 sec
				s = s.replace("\r","").replace("\n","")

				data = unhexlify(s)
				for i in range( 16 ):
					self.addr.write_word( _addr )
					self.data.value = data[2+i]
					time.sleep_ms(1) # Gives the time to set the address
					self.ce.on() # Pulse LOW signal on ROM of 30uS
					self.ce.on()
					self.ce.on() # 20 µSec sharp
					self.ce.on() # 25 µSec
					self.ce.off() # signal is High
					_addr += 1

		finally:
			self.read_led.off()
			# Disable programming mode Mode
			self.oe_prog.off()
			# recover time
			time.sleep_ms( 100 )
			self.data.config( Pin.IN ) # High impedance
			self.ce.on() # Set signal low

			t2 = time.time()
			print( t2-t1, "seconds" )

	def erase( self ):
		""" Just erase the EEPROM """
		self.reset()
		time.sleep_ms(10)
		self.data.config( Pin.IN ) # Read mode
		self.addr.write_word( 0x0000 ) # ensure A9 = Low

		self.oe.value( False ) # Ensure OE is HIGH
		self.addr.write_word( 0xFFFF ) # Ensure A9 is High
		self.oe_prog.on() # Set 12V on OE (programmation mode)
		self.a9_prog.on() # Set 12V on A9 (Erase mode)
		time.sleep_ms( 1 )

		self.ce.on() # Set LOW for 100ms to 500ms to erase
		time.sleep_ms( 500 )
		self.ce.off() # Set HIGH

		time.sleep_ms( 1 )

		# Disable Erase mode
		self.oe_prog.off() # OE as Output Enable
		self.a9_prog.off() # A9 set as address line
		# now oe & A9 are high
		self.oe.value( True ) # Ensure OE is LOW
		self.addr.write_word( 0x0000 ) # ensure A9 = Low
		# Time for recover
		time.sleep_ms( 1 )
		#
		self.ce.value( True ) # Set CE LOW



# ==============================================================================
#  Main script
# ==============================================================================

def show_welcom():
	print( "eeprog - Micropython GLS27SF512 programmer" )
	print( "version", __version__ )
	print( "repo", __repo__ )

def get_command( _prompt ):
	""" return a list with [command, arg1, arg2, argn] """
	sys.stdout.write( "\r%s " % _prompt )
	s = sys.stdin.readline()
	return s.replace("\r","").replace("\n","").split(" ")

def normalise_addr( start_addr, end_addr ):
	try:
		start_addr = eval( cmd[1] )
	except Exception:
		raise Exception("Invalid syntax %s for start_addr" % start_addr )
	if start_addr%16 != 0:
		# take the first correct address below the addr mentionned
		start_addr = start_addr - (start_addr%16)

	# end_addr+1 must be a multiple of 16
	try:
		end_addr = eval( cmd[2] )
	except Exception:
		raise Exception("Invalid syntax %s for end_addr" % end_addr )
	if ((end_addr+1) % 16) != 0:
		# take the next valid address
		end_addr = (end_addr//16)*16 + 15

	return start_addr, end_addr


prog = EProgrammer()
while True:
	try:
		# cmd is a list, command is the first entry, args are the following
		cmd = get_command( ">" )
		if cmd[0] == '':
			continue # just ignore and display the prompt again
		if cmd[0] == "QUIT":
			break
		elif cmd[0] == "V":
			show_welcom()
			continue
		elif cmd[0] in ("T", "R"): # Text_read or Read
			if len(cmd)!= 3:
				raise Exception( "Requires 2 args!" )
			# start_addr must be multiple of 16
			start_addr, end_addr = normalise_addr( cmd[1], cmd[2] ) # Start Addr, End addr
			prog.reset()
			if cmd[0] == "T":
				prog.read_text( start_addr, end_addr )
			else:
				prog.read_fast( start_addr, end_addr )
		elif cmd[0] == "K":
			if len(cmd)!= 3:
				raise Exception( "Requires 2 args!" )
			# start_addr must be multiple of 16
			start_addr, end_addr = normalise_addr( cmd[1], cmd[2] ) # Start Addr, End addr
			prog.reset()
			prog.check_erased( start_addr, end_addr ) # Will raise Exception
		elif cmd[0] == "W":
			if len(cmd)!= 3:
				raise Exception( "Requires 2 args!" )
			start_addr, end_addr = cmd[1], cmd[2] # Start Addr, End addr
			prog.upload( start_addr, end_addr )
		elif cmd[0] == "E":
			prog.erase()
		else:
			raise Exception( "Invalid command %s" % " ".join(cmd))

	except Exception as err:
		print( "[ERROR] %s" % err)
		sys.print_exception( err )
