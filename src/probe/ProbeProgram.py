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
        parser.add_argument("--baud","-b", type=int, default=9600,
            help="Baud rate of the serial port.")
        parser.add_argument("--verbose","-v", action="store_true")
        
        subparsers = parser.add_subparsers()

        test_parser = subparsers.add_parser(pc.CMD_TRY_CONNECT)
        test_parser.set_defaults(func = self.cmdTestOpen)
        test_parser.description = "Test a connection on the specified port"

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
        gpo_parser.add_argument("--clearbit", type=int,choices=range(0,32),
            help="Clear an individual output bit to 0")

        axi_parser = subparsers.add_parser(pc.CMD_AXI)
        axi_parser.set_defaults(func = self.cmdAXI)
        axi_parser.description = "Read and write data via the AXI master bus interface of the probe."
        axi_parser.add_argument("--set-address", type=str)
        axi_parser.add_argument("--get-address", action="store_true")
        axi_parser.add_argument("--auto-inc", type=bool, choices=[True,False])
        axi_parser.add_argument("--get-status", action="store_true")
        axi_parser.add_argument("--read", action="store_true")
        axi_parser.add_argument("--write", type=str)

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


    def cmdAXI(self):
        """
        Interprets commands related to the axi bus.
        """

        # Setup auto incrementing.
        if(self.args.auto_inc != None):

            csr = BitArray(bytes=self.probe.do_AXRDCS(), length=8)
            ae  = csr[-1]

            if(ae and not self.args.auto_inc):
                # We need to clear the autoinc bit
                csr[-1] = 0
                self.probe.do_AXWRCS(csr.bytes)

            elif(not ae and self.args.auto_inc):
                # We need to set the autoinc bit
                csr[-1] = 1
                self.probe.do_AXWRCS(csr.bytes)

        
        # Get the axi master address value
        if(self.args.get_address):
            print("AXI Address: %s"%hex(self.probe.getAXIAddress()))

        # Set the axi master address value
        if(self.args.set_address != None):
            addr = int(self.args.set_address,base=16)
            self.probe.setAXIAddress(addr)


        # Display the current status of the AXI master bus.
        if(self.args.get_status):
            csr = BitArray(bytes=self.probe.do_AXRDCS(), length=8)
            
            ae = csr[pc.AXCS_AE]
            rv = csr[pc.AXCS_RV]
            wv = csr[pc.AXCS_WV]
            
            rr = csr[-7:-6]
            wr = csr[-5:-4]

            print("AXI Status")
            print("Field | Value                   | Value ")
            print("------|-------------------------|---------")
            print(" 1    | Address auto increment  | %d" % ae)
            print(" 2    | Read response valid     | %d" % rv)
            print(" 3    | Write response valid    | %d" % wv)
            print("4:5   | Read response           | %d" % rr.uint)
            print("5:7   | Write Response          | %d" % wr.uint)

        if(self.args.read):
            # Read the current address value?
            csr = BitArray(bytes=self.probe.do_AXRDCS(), length=8)
            csr[1] = 1
            self.probe.do_AXWRCS(csr.bytes)
            data = self.probe.do_RDAXD()
            print("Read data: %h" % data)

        if(self.args.write != None):
            # Perform a write to the current address.
            bits = BitArray(hex = self.args.write)
            self.probe.do_WRAXD(bits.bytes)


    def cmdTestOpen(self):
        """
        Checks if the port is open. Returns 1 if not, 0 if it is open.
        """
        if(self.probe.connected()):
            print("Probe successfully connected on port '%s'" % self.portname)
        else:
            print("Probe not connected")
            return 1

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
            gpo  = (self.probe.do_RDGPO0(),
                    self.probe.do_RDGPO1(),
                    self.probe.do_RDGPO2(),
                    self.probe.do_RDGPO3())
            sys.stdout.write("GPO: ")
            for b in gpo:
                sys.stdout.write("%s " %b.hex())
            print("")
            return 0

        if(self.args.readbit != None):
            print("Reading GPO[%d]" % self.args.readbit)
            bit = self.probe.getGPOBit(self.args.readbit)
            print("GPO[%d] = %s" % (self.args.readbit, bit))
            return 0

        if(self.args.setbit != None):
            bank = int(self.args.setbit / 8)
            bit  = int(self.args.setbit % 8)
            byte = self.probe.getGPOByte(bank)
            bitv = self.probe.getBit(bit, byte)
            
            if(bitv == 0):
                tosend = byte | (1 << (7-bit))
                self.probe.setGPOByte(bank, tosend)

            return 0

        if(self.args.clearbit != None):
            bank = int(self.args.clearbit / 8)
            bit  = int(self.args.clearbit % 8)
            byte = self.probe.getGPOByte(bank)
            bitv = self.probe.getBit(bit, byte)
            
            if(bitv == 1):
                tosend = byte & ~(1 << (7-bit))
                self.probe.setGPOByte(bank, tosend)

            return 0

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
