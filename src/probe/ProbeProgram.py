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

        commands = [
            pc.CMD_TRY_CONNECT,
            pc.CMD_PRINT_REGISTERS
        ]
        
        parser.add_argument("port", type=str,
            help="The name of the TTY/COM port to connect to the probe over.")
        parser.add_argument("command",type=str,
            help="The command to perform with the probe software.",
            choices = commands)
        parser.add_argument("--baud","-b", type=int, default=9600,
            help="Baud rate of the serial port.")
        
        args = parser.parse_args()

        self.portname = args.port
        self.baudrate = args.baud
        self.command  = args.command


    def __init__(self):
        """
        Instance the new program.
        """
        # Parse the command line arguments
        self.__parse_args__()
        # Create the instance of the probe interface
        self.probe = ProbeIfSerial()


    def testOpen(self):
        """
        Checks if the port is open. Returns 1 if not, 0 if it is open.
        """
        if(self.probe.connected()):
            print("Probe successfully connected on port '%s'" % self.portname)
            return 0
        else:
            print("Probe not connected")
            return 1


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

        tr = 0
        
        if(self.command == pc.CMD_PRINT_REGISTERS):
            tr = self.probe.printRegisters()
        elif(self.command == pc.CMD_TRY_CONNECT):
            tr = self.testOpen()

        return tr


if(__name__ == "__main__"):
    program = ProbeProgram()
    sys.exit(program.main())
