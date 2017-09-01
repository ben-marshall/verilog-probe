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
