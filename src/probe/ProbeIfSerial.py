#!/usr/bin/python3

import os
import sys

import serial

import ProbeCommon as pc
from   ProbeInterface import ProbeInterface

class ProbeIfSerial(ProbeInterface):
    """
    Class which implements the ProbeInterface class.
    """

    def __init__(self, verbose=False):
        """
        Create the interface.
        """
        self.port       = serial.Serial()
        self.verbose    = verbose
    
    def open(self, portname, baud = 9600, timeout=1000):
        """
        Open the serial interface with the supplied name.
        """
        self.port.port      = portname
        self.port.baudrate  = baud
        self.port.timeout   = timeout
        self.port.bytesize  = serial.EIGHTBITS
        self.port.xonxoff   = False
        self.port.open()

    def connected(self):
        """
        Have we successfully opened a connection to the port?
        """
        return self.port.is_open


    def __send__(self,val):
        """
        Send one byte to the probe.
        """
        assert(len(val) == 1)
        assert(type(val) == bytes)
        v = int.from_bytes(val,byteorder="little")
        if(self.verbose):
            pc.color_stdout("GREEN")
            print(">> %s\t - %s\t - %d"% (hex(v),bin(v),v))
            pc.color_stdout("RESET")
        self.port.write(val)


    def __recv__(self):
        """
        Read one byte from the probe.
        """
        data = self.port.read(size=1)
        v = int.from_bytes(data, byteorder="little")
        if(self.verbose):
            pc.color_stdout("RED")
            print("<< %s\t - %s\t - %d"% (hex(v),bin(v),v))
            pc.color_stdout("RESET")
        return data

    def do_RDGPI0(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPI0))
        return self.__recv__()

    def do_RDGPI1(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPI1))
        return self.__recv__()

    def do_RDGPI2(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPI2))
        return self.__recv__()

    def do_RDGPI3(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPI3))
        return self.__recv__()

    def do_RDGPO0(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPO0))
        return self.__recv__()

    def do_RDGPO1(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPO1))
        return self.__recv__()

    def do_RDGPO2(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPO2))
        return self.__recv__()

    def do_RDGPO3(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDGPO3))
        return self.__recv__()

    def do_WRGPO0(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRGPO0))
        self.__send__(value)
        return None

    def do_WRGPO1(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRGPO1))
        self.__send__(value)
        return None

    def do_WRGPO2(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRGPO2))
        self.__send__(value)
        return None

    def do_WRGPO3(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRGPO3))
        self.__send__(value)
        return None

    def do_RDAXA0(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDAXA0))
        return self.__recv__()

    def do_RDAXA1(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDAXA1))
        return self.__recv__()

    def do_RDAXA2(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDAXA2))
        return self.__recv__()

    def do_RDAXA3(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDAXA3))
        return self.__recv__()

    def do_WRAXA0(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRAXA0))
        self.__send__(value)
        return None

    def do_WRAXA1(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRAXA1))
        self.__send__(value)
        return None

    def do_WRAXA2(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRAXA2))
        self.__send__(value)
        return None

    def do_WRAXA3(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRAXA3))
        self.__send__(value)
        return None

    def do_AXIRB0 (self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXIRB0))
        return self.__recv__()

    def do_AXIRB1 (self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXIRB1))
        return self.__recv__()

    def do_AXIRB2 (self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXIRB2))
        return self.__recv__()

    def do_AXIRB3 (self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXIRB3))
        return self.__recv__()

    def do_AXIWB0 (self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXIWB0))
        self.__send__(value)
        return None

    def do_AXIWB1 (self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXIWB1))
        self.__send__(value)
        return None

    def do_AXIWB2 (self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXIWB2))
        self.__send__(value)
        return None

    def do_AXIWB3 (self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXIWB3))
        self.__send__(value)
        return None

    def do_AXIRDRC(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXIRDRC))
        return self.__recv__()

    def do_AXIWRRC(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXIWRRC))
        self.__send__(value)
        return None

    def do_AXIRDWC(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXIRDWC))
        return self.__recv__()

    def do_AXIWRWC(self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXIWRWC))
        self.__send__(value)
        return None



