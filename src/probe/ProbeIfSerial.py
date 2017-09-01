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

    def __init__(self):
        """
        Create the interface.
        """
        self.port       = serial.Serial()
    
    def open(self, portname, baud = 9600, timeout=1):
        """
        Open the serial interface with the supplied name.
        """
        self.port.port      = portname
        self.port.baudrate  = baud
        self.port.timeout   = timeout
        self.port.bytesize  = serial.EIGHTBITS
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
        v = str(val, encoding="ascii")
        pc.color_stdout(col = 32)
        sys.stdout.write("%s"%v)
        sys.stdout.flush()
        pc.nocolor_stdout()
        self.port.write(val)


    def __recv__(self):
        """
        Read one byte from the probe.
        """
        data = self.port.read(size=1)
        v = str(data,encoding="ascii")
        pc.color_stdout(col = 36)
        sys.stdout.write("%s"%v)
        sys.stdout.flush()
        pc.nocolor_stdout()
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
        self.__send__(bytes(pc.PROBE_CMD_RDGPO2))
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

    def do_RDAXD (self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_RDAXD))
        return self.__recv__()

    def do_WRAXD (self, value):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_WRAXD))
        self.__send__(value)
        return None

    def do_AXRDCS(self):
        """
        Perform the command '' and return the result.
        """
        self.__send__(bytes(pc.PROBE_CMD_AXRDCS))
        return self.__recv__()

    def do_AXWRCS(self, AE=True):
        """
        Perform the command '' and return the result.
        """
        assert(len(value) == 1)
        assert(type(value) == bytes)
        self.__send__(bytes(pc.PROBE_CMD_AXWRCS))
        self.__send__(value)
        return None


