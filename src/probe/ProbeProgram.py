#!/usr/bin/python3

"""
Software to communicate with a simple UART Probe Module.
"""

import os
import sys
import random
import argparse

from   bitstring import BitArray

import ProbeCommon as pc
from   ProbeInterface import ProbeInterface
from   ProbeIfSerial  import ProbeIfSerial

class ProbeProgram(object):
    """
    Program class which holds all program state and variables.
    """

    def __parse_args__(self):
        """
        Responsible for parsing and returning all command line arguments.
        """
        parser = argparse.ArgumentParser(description=__doc__)
        
        parser.add_argument("port", type=str,
            help="The name of the TTY/COM port to connect to the probe over.")
        parser.add_argument("--baud","-b", type=int, default=57600,
            help="Baud rate of the serial port.")
        parser.add_argument("--verbose","-v", action="store_true")
        
        subparsers = parser.add_subparsers()

        test_parser = subparsers.add_parser(pc.CMD_TRY_CONNECT)
        test_parser.set_defaults(func = self.cmdTestOpen)
        test_parser.description = "Test a connection on the specified port"

        demo_parser = subparsers.add_parser(pc.CMD_DEMO)
        demo_parser.set_defaults(func = self.cmdDemo)
        demo_parser.description = "Run a demo script using the AXI master"
        
        file_parser = subparsers.add_parser(pc.CMD_FILE)
        file_parser.set_defaults(func = self.cmdFile)
        file_parser.description = "Read and write files into & out of the probe"
        file_parser.add_argument("file", type=str,
            help="file to be read or written")
        file_parser.add_argument("--read", action="store_true",
            help="Read probe memory into this file")
        file_parser.add_argument("--write", action="store_true",
            help="Write this file into this address")
        file_parser.add_argument("--address", type=str,
            help="Set the AXI address to this value before reading/writing")
        file_parser.add_argument("--length", type=int, default=8,
            help="How many words (4 bytes) to read or write?")

        print_regs_parser = subparsers.add_parser(pc.CMD_PRINT_REGISTERS)
        print_regs_parser.set_defaults(func = self.cmdPrintRegisters)
        print_regs_parser.description = "Print probe register values"

        gpi_parser = subparsers.add_parser(pc.CMD_GPI)
        gpi_parser.set_defaults(func = self.cmdGPI)
        gpi_parser.description = "Allows for reading of the general purpose inputs"
        gpi_single = gpi_parser.add_mutually_exclusive_group(required=True)
        gpi_single.add_argument("--readbit", type=int,choices=range(0,32),
            help="Read an individual input and print its value")
        gpi_single.add_argument("--all", action="store_true",
            help="Print the values of all general purpose inputs.")

        gpo_parser = subparsers.add_parser(pc.CMD_GPO)
        gpo_parser.set_defaults(func = self.cmdGPO)
        gpo_parser.description = "Allows control of the general purpose outputs"
        gpo_parser.add_argument("--readall", action="store_true",
            help="Print the values of all general purpose outputs.")
        gpo_parser.add_argument("--readbit", type=int,choices=range(0,32),
            help="Read an individual output bit and print its value")
        gpo_parser.add_argument("--setbit", type=int,choices=range(0,32),
            help="Set an individual output bit to 1")
        gpo_parser.add_argument("--setall", action="store_true",
            help="Set all general purpose outputs.")
        gpo_parser.add_argument("--clearbit", type=int,choices=range(0,32),
            help="Clear an individual output bit to 0")
        gpo_parser.add_argument("--clearall", action="store_true",
            help="Clear all general purpose outputs.")

        axi_parser = subparsers.add_parser(pc.CMD_AXI)
        axi_parser.set_defaults(func = self.cmdAXI)
        axi_parser.description = "Read and write data via the AXI master bus interface of the probe."
        axi_parser.add_argument("--set-address", type=str,
            help="Set the AXI address to any 32-bit value.")
        axi_parser.add_argument("--get-address", action="store_true",
            help="Read the current AXI address.")
        axi_parser.add_argument("--auto-inc", type=int, choices=[0,1],
            help="Turn address auto-incremnting on/off")
        axi_parser.add_argument("--get-status", action="store_true",
            help="Return the current status of the AXI bus master.")
        axi_parser.add_argument("--read", action="store_true",
            help="Perform an AXI read")
        axi_parser.add_argument("--write", type=str,
            help="Perform an AXI write")

        args = parser.parse_args()
        
        self.probe.verbose = args.verbose
        self.portname = args.port
        self.baudrate = args.baud
        self.args = args


    def __init__(self):
        """
        Instance the new program.
        """
        # Create the instance of the probe interface
        self.probe = ProbeIfSerial()
        # Parse the command line arguments
        self.__parse_args__()


    def cmdFile(self):
        """
        Read and write files into and out of probe memory.
        """
        assert(not (self.args.read and self.args.write))

        if(self.args.address != None):
            print("Setting AXI address: %s" % self.args.address)
            self.probe.set_address(self.args.address)

        openmode = None
        if(args.read):
            openmode = "rb"
        else:
            opemode  = "wb"

        with open(args.file,openmode) as fh:

            for i in range(0,self.args.length):

                if(args.read):
                    self.probe.doRead(autoInc=True)
                    data = getAXIReadData()
                else:
                    self.probe.setAXIWriteData("00000000")
                    self.probe.doWrite(auto_inc=True)



    def cmdAXI(self):
        """
        Interprets commands related to the axi bus.
        """

        # Setup auto incrementing.
        if(self.args.auto_inc != None):

            csr = BitArray(bytes=self.probe.do_AXIRDRC(), length=8)
            ae  = csr[-2]
            print(csr)

            if(ae and self.args.auto_inc == 0):
                # We need to clear the autoinc bit
                print("Clear address auto-increment")
                csr[-2] = 0
                self.probe.do_AXIWRRC(csr.bytes)

            elif(not ae and self.args.auto_inc == 1):
                # We need to set the autoinc bit
                print("Set address auto-increment")
                csr[-2] = 1
                self.probe.do_AXIWRRC(csr.bytes)
            print(csr)

        
        # Get the axi master address value
        if(self.args.get_address):
            print("AXI Address: %s"%hex(self.probe.getAXIAddress()))

        # Set the axi master address value
        if(self.args.set_address != None):
            addr = int(self.args.set_address,base=16)
            self.probe.setAXIAddress(addr)


        # Display the current status of the AXI master bus.
        if(self.args.get_status):
            rs = BitArray(bytes=self.probe.do_AXIRDRC())
            ws = BitArray(bytes=self.probe.do_AXIRDRC())

            print("Read Status:")
            print(" - Response Valid: %s" % rs[ 4 ])
            print(" - Response Value: %d" % rs[0:1].uint)

            print("Write Status:")
            print(" - Response Valid: %s" % ws[ 4 ])
            print(" - Response Value: %d" % ws[0:1].uint)

            print ("Address auto incremnet: %s" % rs[-2])

        if(self.args.read):
            # Read the current address value?
            csr = BitArray(bytes=self.probe.do_AXIRDRC(), length=8)
            csr[1] = 1
            self.probe.do_AXIWRRC(csr.bytes)
            data = self.probe.getAXIReadData()
            print("Read data: %h" % data)

        if(self.args.write != None):
            # Perform a write to the current address.
            bits = BitArray(hex = self.args.write)
            print("Setting write data: %h" % self.args.write)
            self.probe.setAXIWriteData(bits)
            print("Performing write.")
            self.probe.do_AXIWRWC(bytes(1))


    def cmdDemo(self):
        """
        Runs a very simple demo program.
        """
        auto_inc     = False
        base_address = int("40000008",base=16)
        print("Setting Base Address: %s" % hex(base_address))
        self.probe.setAXIAddress(base_address)

        print("Setting address auto increment: %s" % str(auto_inc))
        self.probe.setAutoIncrement(auto_inc)
        
        csr = self.probe.do_AXIRDRC()
        print("Pre-Read Response Value: %s" % csr)
        
        # Read the switches

        self.probe.doRead()

        csr = self.probe.do_AXIRDRC()
        print("Read Response: %s" % csr)

        sys.stdout.write("Read Data: ")
        rdata = self.probe.getAXIReadData()
        print("dec: %d, hex: %s, bin: %s" % (rdata,hex(rdata),bin(rdata)))

        sys.stdout.write("New AXI Address value: ")
        data = self.probe.getAXIAddress()
        print("dec: %d, hex: %s, bin: %s" % (data,hex(data),bin(data)))

        #  Write the LEDS
        base_address = int("40000000",base=16)
        print("Setting Base Address: %s" % hex(base_address))
        self.probe.setAXIAddress(base_address)

        # Set the write data
        print("Setting Write data: %s" % hex(rdata))
        self.probe.setAXIWriteData(rdata)
        self.probe.doWrite()
        csr = self.probe.do_AXIRDWC()
        print("Write Response: %s" % csr)

        return 0


    def cmdTestOpen(self):
        """
        Checks if the port is open. Returns 1 if not, 0 if it is open.
        """
        if(self.probe.connected()):
            print("Probe successfully connected on port '%s'" % self.portname)
        else:
            print("Probe not connected")
            return 1
        
        # Read the general purpose inputs
        print("General Purpose Inputs:")
        for i in range(0,4):
            v = self.probe.getGPIByte(i)
            print("GPI[%d] bank %s" % (i,v))

        # Read the general purpose outputs
        print("General Purpose Outputs:")
        for i in range(0,4):
            tw = BitArray(hex=hex(random.randint(0,255)))[-8:].bytes
            print("Write %s to GPO bank %d" %(tw,i))
            self.probe.setGPOByte(i,tw)
            v = self.probe.getGPOByte(i)
            print("Read back %s from GPO bank %d" % (v,i))
            if(v != tw):
                print("[ERROR] Written value does not match read value")
                return 1

        # Write a random number to the AXI Address registers.
        tw = random.randint(0,2**32-1)
        print("Writing to AXI address register.")
        print("> %s" % hex(tw))
        print("> %s" % bin(tw))

        self.probe.setAXIAddress(tw)
        print(" ")

        # Get the AXI address back anc check it matches.
        rb = self.probe.getAXIAddress()
        print("Read back value: %s" % hex(rb))
        print("> %s" % hex(rb))
        print("> %s" % bin(rb))

        if(rb != tw):
            print("[ERROR] Read back data is not the same as what we wrote.")
            return 1
        
        print("[TEST SUCCESSFUL]")
        return 0


    def cmdPrintRegisters(self):
        """
        Print the values of the registers on the probe side.
        """
        return self.probe.printRegisters()


    def cmdGPI(self):
        """
        Interracts with the general purpose inputs based on the command
        line arguments to the program.
        """

        if(self.args.all):
            # print all of the general purpose inputs
            gpi  = (self.probe.do_RDGPI0(),
                    self.probe.do_RDGPI1(),
                    self.probe.do_RDGPI2(),
                    self.probe.do_RDGPI3())
            sys.stdout.write("GPI: ")
            for b in gpi:
                sys.stdout.write("%s " %b.hex())
            print("")
            return 0

        else:
            # print a single general purpose input value.
            bit =  self.probe.getGPIBit(args.readbit)
            print("GPI[%d] = %s" % (self.args.input, bit))
            return 0


    def cmdGPO(self):
        """
        Interract with the general purpose outputs.
        """
        if(self.args.readall):
            # print all of the general purpose outputs
            gpo  = (self.probe.do_RDGPO3(),
                    self.probe.do_RDGPO2(),
                    self.probe.do_RDGPO1(),
                    self.probe.do_RDGPO0())
            sys.stdout.write("GPO: ")
            for b in gpo:
                sys.stdout.write("%s " %b.hex())
            print("")
            return 0

        if(self.args.clearall):
            # Clear all bytes to zero.
            print("Clearing all GPOs")
            for i in range(0,4):
                self.port.setGPOByte(i,bytes(0))
        
        if(self.args.setall):
            # Set all bytes to one.
            print("Setting all GPOs")
            for i in range(0,4):
                self.port.setGPOByte(i,bytes(255))

        if(self.args.readbit != None):
            print("Reading GPO[%d]" % self.args.readbit)
            bit = self.probe.getGPOBit(self.args.readbit)
            print("GPO[%d] = %s" % (self.args.readbit, bit))
            return 0

        if(self.args.setbit != None):
            bank = int(self.args.setbit / 8)
            bit  = int(self.args.setbit % 8)
            byte = BitArray(bytes=self.probe.getGPOByte(bank),length=8)
            bitv = byte[7-bit]
            
            if(bitv == 0):
                byte[7-bit] = 1
                self.probe.setGPOByte(bank, byte.bytes)

            return 0

        if(self.args.clearbit != None):
            bank = int(self.args.clearbit / 8)
            bit  = int(self.args.clearbit % 8)
            byte = BitArray(bytes=self.probe.getGPOByte(bank),length=8)
            bitv = byte[7-bit]
            
            if(bitv == 1):
                byte[7-bit] = 0
                self.probe.setGPOByte(bank, byte.bytes)

            return 0


    def main(self):
        """
        Main entry point function for the program.
        """
        try:
            self.probe.open(self.portname, baud=self.baudrate,
                timeout=None)
        except Exception as e:
            print("[ERROR] Could not open port '%s'",self.portname)
            print(e)
            return 1

        tr = self.args.func()
        
        return tr


if(__name__ == "__main__"):
    program = ProbeProgram()
    sys.exit(program.main())
