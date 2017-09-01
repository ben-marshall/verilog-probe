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
        gpi_single.add_argument("--input", type=int,choices=range(0,31),
            help="Read an individual input and print its value")
        gpi_single.add_argument("--all", action="store_true",
            help="Print the values of all general purpose inputs.")

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
            bank = int(self.args.input / 8)
            biti = self.args.input % 8
            bval = None

            if(bank == 0):
                bval = self.probe.do_RDGPI0()
            elif(bank == 1):
                bval = self.probe.do_RDGPI1()
            elif(bank == 2):
                bval = self.probe.do_RDGPI2()
            elif(bank == 3):
                bval = self.probe.do_RDGPI3()
            
            hexval = bval.hex()
            intval = int(hexval,base=16)
            binval = bin(intval)[2:]
            bit    = binval[7-biti]
            
            print("GPI[%d] = %s" % (self.args.input, bit))
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
