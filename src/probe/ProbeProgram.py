#!/usr/bin/python3

import os
import sys

import  ProbeCommon as pc
from    ProbeInterface import ProbeInterface
from    ProbeIfSerial  import ProbeIfSerial

class ProbeProgram(object):
    """
    Program class which holds all program state and variables.
    """


    def __init__(self):
        """
        Instance the new program.
        """
        self.__parse_args__()

        self.probe = ProbeIfSerial()


    def __parse_args__(self):
        """
        Responsible for parsing and returning all command line arguments.
        """


    def main(self):
        """
        Main entry point function for the program.
        """

        return 0


if(__name__ == "__main__"):
    program = ProbeProgram()
    sys.exit(program.main())
