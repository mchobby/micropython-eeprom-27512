#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" FlashRom is a Python3 PC tool to use in conjonction with MicroPython eeprog.py EEPROM programmer."

Usage:
	flashrom dump <from_addr> <to_addr> <local_filename> [--device=<serial>]
	flashrom upload <from_addr> <to_addr> <bin_file>
	flashrom view <from_addr> <to_addr> [--device=<serial>]
	flashrom empty <from_addr> <to_addr> [--device=<serial>]
	flashrom erase [--device=<serial>]
	flashrom version [--device=<serial>]
"""

from docopt import docopt
from binascii import hexlify, unhexlify
import serial # pySerial
import sys
import time

class Application:
	def __init__( self, _serial ):
		self.ser = _serial # Initialized Pi Serial Instance

	def crc8_itu(self, msg):
		crc = 0
		for byte in msg:
			crc ^= byte
			for _ in range(8):
				crc = (crc << 1) ^ 7 if crc & 0x80 else crc << 1
			crc &= 0xff
		return crc ^ 0x55

	def assert_prompt( self ):
		""" Check that EEPROM programmer is ready to receive a command """
		self.ser.write( ('\n').encode('ASCII') ) # Sending a carriage return
		for i in range(3):
			l = self.readline() # soould return the prompt but can contains an invalid command
			if l==None:
				continue
			if '> ' in l:
				return
		# @ this line, no prompt was detected
		raise Exception("No prompt received from programming board")

	def send_command( self, command ):
		""" Send a command to the Flash Programmer """
		self.assert_prompt()
		return self.ser.write( ('%s\n'%(command)).encode('ASCII') )

	def readline( self, retry=0 ):
		""" Read a line from serial port ( strip \r & \n ).
		Returns a string or None """
		i = 0
		while i<=retry:
			l = ser.readline() # Timeout (see constructor)
			if len(l)==0:
				i += 1
				continue
			return l.decode('UTF8').replace('\r','').replace('\n','')
		return None

	def dump_to( self, from_addr, to_addr, _f ):
		""" Dump EEPROM memory to a given file stream """
		app.send_command('R %s %s' % (from_addr,to_addr) )
		s = self.ser.readline().decode('UTF8').replace('\n','').replace('\r','')
		#print( s )
		while (len(s)>0) and not( '> ' in s ):
			data = unhexlify( s )
			if len(data)!=19 :
				raise Exception( 'Invalid data length for %s , 19 bytes expected!' % s )
			crc = self.crc8_itu( data[:18])
			if crc != data[18]:
				raise Exception( "Invalid CRC check for %s" % s )
			#print( "%s -> %s" % (len(data[2:18]), data[2:18]) )
			_f.write( data[2:18] )
			s = self.ser.readline().decode('UTF8').replace('\n','').replace('\r','')
			#print(s)

	def upload_bin( self, from_addr, to_addr, _f ):
		""" Upload file stream into EEPROM memory from from_addr to to_addr. """
		app.send_command('W %s %s' % (from_addr,to_addr) )
		data = bytearray(19)
		_addr = eval( from_addr )
		_to_addr = eval( to_addr )
		while _addr <= _to_addr:
			if _addr%256 == 0:
				print( "Writing at 0x%04X" % _addr )
				time.sleep( 0.100 )

			data[0] = (_addr >> 8 ) & 0xFF
			data[1] = _addr & 0xFF
			i = 0
			while i < 16:
				buf1 = _f.read(1)
				# Replace with 0x00 when reading outside the file scope
				if len(buf1) == 0:
					data[2+i] = 0x00
				else:
					data[2+i] = buf1[0]
				i += 1
				_addr += 1 # Current address
			# Calculate the CRC
			data[18] = self.crc8_itu( data[:18] )

			# Wait the = to send the packet
			buf1 = self.ser.read(1)
			retry = 0
			# 61="=" , 62=">", 91="["
			while (len(buf1)<=0) and not(buf1[0] in (61,62,91)) and (retry<3):
				time.sleep(0.500)
				retry+=1
				buf1 = self.ser.read(1)
			if len(buf1)==0:
				raise Exception( "= or > or [ sign not received for sending next packet")
			if buf1[0]==91: # [
				print( "Error detected! Exit upload" )
				s=self.ser.readline()
				while len(s)>0:
					print( s.decode('UTF8').replace("\r","").replace("\n","") )
					s=self.ser.readline()
				return
			if buf1[0]==62: # >
				print( "Command prompt detected! Exit upload" )
				return

			self.ser.write( hexlify(data) ) # already bytes
			self.ser.write( bytes([10]) )
			#print( hexlify(data) )
		return

	def erase( self ):
		app.send_command('E')

# ==============================================================================
#
# ==============================================================================


if __name__ == "__main__":
	arguments = docopt( __doc__, version = 'FlashRom 0.1' )
	# print( arguments )
	if arguments['--device'] == None:
		_devname = '/dev/ttyACM0'
	else:
		_devname = arguments['--device']

	ser = serial.Serial( _devname, 115200, timeout=1 ) # May raise SerialException
	app = Application( ser )

	if arguments['view'] == True:
		# T = read text
		app.send_command('T %s %s' % (arguments['<from_addr>'],arguments['<to_addr>']) )
		while True:
			l = app.readline() # Retry do also increase total timeout
			if (l==None) or ('> ' in l):
				break
			print( l )
		sys.exit(0)


	if arguments['version'] == True:
		app.send_command( 'V' ) # Get version
		while True:
			l = app.readline()
			if l==None:
				break
			print( l )
		sys.exit(0)

	if arguments['empty'] == True:
		# K = check empty
		app.send_command('K %s %s' % (arguments['<from_addr>'],arguments['<to_addr>']) )
		while True:
			l = app.readline( retry=3 ) # Retry do also increase total timeout
			if (l==None) or ('> ' in l):
				break
			print( l )
		sys.exit(0)

	if arguments['dump'] == True:
		# R = read binary
		with open( arguments['<local_filename>'], "wb" ) as f: # Write binary file
			app.dump_to( arguments['<from_addr>'], arguments['<to_addr>'], f )
		print( 'file %s created' % arguments['<local_filename>'] )
		sys.exit(0)

	if arguments['upload'] == True:
		# R = read binary
		with open( arguments['<bin_file>'], "rb" ) as f: # read binary file
			app.upload_bin( arguments['<from_addr>'], arguments['<to_addr>'], f )
		print( 'file %s uploaded' % arguments['<bin_file>'] )
		sys.exit(0)

	if arguments['erase'] == True:
		# R = read binary
		app.erase()
		print( 'EEProm erased!' )
		# Display view bytes to show begin of EEPROM
		app.send_command( 'T 0x000 0x0100' )
		while True:
			l = app.readline() # Retry do also increase total timeout
			if (l==None) or ('> ' in l):
				break
			print( l )

		sys.exit(0)

	# compile_url( arguments['<wiki_link>'], arguments['<tuto_page_url>'] )
