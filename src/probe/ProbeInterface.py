#!/usr/bin/python3

import os
import sys

from   bitstring import BitArray

import ProbeCommon as pc

class ProbeInterface(object):
    """
    Interface class which implements stub versions of all functions we
    expect the probe to implement. This allows us to abstract the functionality
    of the probe away from per-system details of how we communicate with
    it.
    """

    def __init__(self):
        """
        Create the interface.
        """

    def printRegisters(self):
        """
        Reads all information it can from the probe and prints it to the
        terminal.
        """

        if(not self.connected()):
            return 1
        
        gpi  = (self.do_RDGPI0(),
                self.do_RDGPI1(),
                self.do_RDGPI2(),
                self.do_RDGPI3())
        
        gpo  = (self.do_RDGPO0(),
                self.do_RDGPO1(),
                self.do_RDGPO2(),
                self.do_RDGPO3())
        
        axi_a= (self.do_RDAXA0(),
                self.do_RDAXA1(),
                self.do_RDAXA2(),
                self.do_RDAXA3())

        axi_d= (self.getAXIReadData(),)
        
        rctrl = (self.do_AXIRDRC(),)
        wctrl = (self.do_AXIRDWC(),)

        print("\nProbe Registers:")
        print("\tGPI   : %s %s %s %s" % gpi   )
        print("\tGPO   : %s %s %s %s" % gpo   )
        print("\tAXI A : %s %s %s %s" % axi_a )
        print("\tAXI D : %s"          % axi_d )
        print("\tRD Ctl: %s"          % rctrl )
        print("\tWR Ctl: %s"          % wctrl )

        return 0

    def getAXIAddress(self):
        """
        Return the 32-bit AXI address
        """
        axi_a = self.do_RDAXA0() + self.do_RDAXA1() + self.do_RDAXA2() + self.do_RDAXA3()
        address = int.from_bytes(axi_a, byteorder="little")
        return address

    def setAXIAddress(self, value):
        """
        Set the address of the AXI bus.
        """
        bits = BitArray(hex=hex(value))
        b0 = bits[-8:].bytes 
        b1 = bits[-16:-8].bytes 
        b2 = bits[-24:-16].bytes 
        b3 = bits[-32:-24].bytes 
        self.do_WRAXA0(b0)
        self.do_WRAXA1(b1)
        self.do_WRAXA2(b2)
        self.do_WRAXA3(b3)


    def getAXIReadData(self):
        """
        Return the most recently read value from the AXI bus.
        """
        data = self.do_AXIRB0() + self.do_AXIRB1() + self.do_AXIRB2() + self.do_AXIRB3()
        data = int.from_bytes(data, byteorder="little")
        return data

    def doRead(self):
        """
        Perform a single read transaction at the current address
        """
        csr = BitArray(bytes=self.do_AXIRDRC(), length=8)
        csr[-1] = 1
        self.do_AXIWRRC(csr.bytes)

    def doWrite(self):
        """
        Perform a single write transaction at the current address
        """
        csr = BitArray(bytes=self.do_AXIRDWC(), length=8)
        csr[-1] = 1
        self.do_AXIWRWC(csr.bytes)

    def setAutoIncrement(self, ae):
        """
        Set the auto incrmenet value for addresses when we do reads/writes
        """
        csr = BitArray(bytes=self.do_AXIRDRC(), length=8)
        csr[-2] = ae
        self.do_AXIWRRC(csr.bytes)

    def setAXIWriteData(self, value):
        """
        Set the data to be written on the AXI master bus.
        """
        hexval = hex(value)[2:]
        while(len(hexval)<8):
            hexval = "0"+hexval
        hexval = "0x"+hexval
        bits = BitArray(hex=hexval)
        b0 = bits[-8:].bytes 
        b1 = bits[-16:-8].bytes 
        b2 = bits[-24:-16].bytes 
        b3 = bits[-32:-24].bytes 
        self.do_AXIWB0(b0)
        self.do_AXIWB1(b1)
        self.do_AXIWB2(b2)
        self.do_AXIWB3(b3)


    def getGPIBit(self, bit):
        """
        Return the value of a single bit from the GPIs
        """
        bank = int(bit / 8)
        biti = int(bit % 8)
        byte = self.getGPIByte(bank)
        bit  = self.getBit(biti,byte)
        return bit
    
    def getGPOBit(self, bit):
        """
        Return the value of a single bit from the GPOs
        """
        bank = int(bit / 8)
        biti = int(bit % 8)
        byte = self.getGPOByte(bank)
        bit  = self.getBit(biti,byte)
        return bit
    
    def getGPOByte(self, idx):
        """
        Return the gpO byte addressed by idx.
        """
        if(idx == 0):
            return self.do_RDGPO0()
        elif(idx == 1):
            return self.do_RDGPO1()
        elif(idx == 2):
            return self.do_RDGPO2()
        elif(idx == 3):
            return self.do_RDGPO3()

    def setGPOByte(self, idx, val):
        """
        Return the gpO byte addressed by idx.
        """
        if(idx == 0):
            return self.do_WRGPO0(val)
        elif(idx == 1):
            return self.do_WRGPO1(val)
        elif(idx == 2):
            return self.do_WRGPO2(val)
        elif(idx == 3):
            return self.do_WRGPO3(val)

    def getGPIByte(self, idx):
        """
        Return the gpi byte addressed by idx.
        """
        if(idx == 0):
            return self.do_RDGPI0()
        elif(idx == 1):
            return self.do_RDGPI1()
        elif(idx == 2):
            return self.do_RDGPI2()
        elif(idx == 3):
            return self.do_RDGPI3()

    def getBit(self, biti, bval):
        """
        Return a single bit of a byte
        """

        hexval = bval.hex()
        intval = int(hexval,base=16)
        binval = bin(intval)[2:]
        while(len(binval) < 8):
            binval = "0"+binval
        bit    = binval[7-biti]

        return int(bit)
    
    # -----------------------------------------------------------------------
    # It is expected that functions below this point are overriden. They are
    # deliberately left as stubs.
    # -----------------------------------------------------------------------
    
    def connected(self):
        """
        Have we successfully opened a connection to the probe
        """
        return True

    def do_RDGPI0(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPI1(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPI2(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPI3(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPO0(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPO1(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPO2(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDGPO3(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRGPO0(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRGPO1(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRGPO2(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRGPO3(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDAXA0(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDAXA1(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDAXA2(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_RDAXA3(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRAXA0(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRAXA1(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRAXA2(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRAXA3(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIRB0 (self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIRB1 (self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIRB2 (self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIRB3 (self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIWB0 (self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIWB1 (self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIWB2 (self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIWB3 (self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIRDRC(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIWRRC(self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIRDWC(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXIWRWC(self, value):
        """
        Perform the command '' and return the result.
        """
        return None


