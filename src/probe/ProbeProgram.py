#!/usr/bin/python3

"""
Software to communicate with a simple UART Probe Module.
"""

import os
import sys
import argparse

import  ProbeCommon as pc
from    ProbeInterface import ProbeInterface
from    ProbeIfSerial  import ProbeIfSerial

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

        args = parser.parse_args()

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


    def cmdTestOpen(self):
        """
        Checks if the port is open. Returns 1 if not, 0 if it is open.
        """
        if(self.probe.connected()):
            print("Probe successfully connected on port '%s'" % self.portname)
            return 0
        else:
            print("Probe not connected")
            return 1


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
