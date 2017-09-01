#!/usr/bin/python3

import os
import sys

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

        axi_d= (self.do_RDAXD(),)
        
        ctrl = (self.do_AXRDCS(),)

        print("\nProbe Registers:")
        print("\tGPI   : %s %s %s %s" % gpi   )
        print("\tGPO   : %s %s %s %s" % gpo   )
        print("\tAXI A : %s %s %s %s" % axi_a )
        print("\tAXI D : %s"          % axi_d )
        print("\tCTRL  : %s"          % ctrl  )

        return 0

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

    def do_RDAXD (self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_WRAXD (self, value):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXRDCS(self):
        """
        Perform the command '' and return the result.
        """
        return None

    def do_AXWRCS(self, AE=True):
        """
        Perform the command '' and return the result.
        """
        return None

