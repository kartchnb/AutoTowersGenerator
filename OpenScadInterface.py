import glob
import os
import platform
import subprocess

from UM.Logger import Logger
from UM.Message import Message



class OpenScadInterface:
    OpenScadPath = None



    def __init__(self):
        # Determine the Operating system being used
        system = platform.system()
        Logger.log('d', f'Platform is reported as "{system}"')

        # Set a default OpenSCAD path (should work for Linux)
        self.OpenScadPath = 'openscad'

        # This path for Macintosh was borrowed from Thopiekar's OpenSCAD Integration plugin (https://thopiekar.eu/cura/cad/openscad)
        # I have no way of verifying it works...
        if system == 'Darwin':
            self.OpenScadPath = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

        # For Windows, OpenSCAD should be installed in the Program Files folder
        elif system == 'Windows':
            program_files_path = f'"{os.path.join(os.getenv("PROGRAMFILES"), "OpenSCAD", "openscad.exe")}"'
            program_files_x86_path = f'"{os.path.join(os.getenv("PROGRAMFILES(X86)"), "OpenSCAD", "openscad.exe")}"' # This is just in case - OpenSCAD should never be installed here
            if os.path.isfile(program_files_path):
                self.OpenScadPath = program_files_path
            elif os.path.isfile(program_files_x86_path):
                self.OpenScadPath = program_files_x86_path

        Logger.log('d', f'OpenSCAD path is set to {self.OpenScadPath}')

        self.errorMessage = ''



    def GenerateStl(self, inputFilePath, parameters, outputFilePath):
        '''Execute an OpenSCAD file with the given parameters to generate a model'''
        # Build the OpenSCAD command
        command = self.GenerateOpenScadCommand(inputFilePath, parameters, outputFilePath)
        command_single_line = ' '.join(command)
        Logger.log('d', f'Executing command: {command_single_line}')

        # Execute the OpenSCAD command and capture the error output
        # Output in stderr does not necessarily indicate an error - OpenSCAD seems to routinely output to stderr
        self.errorMessage = subprocess.run(command, capture_output=True, text=True).stderr.strip()



    def  GenerateOpenScadCommand(self, inputFilePath, parameters, outputFilePath):
        '''Generate an OpenSCAD command from an input file path, parameters, and output file path'''

        # Start the command array with the OpenSCAD command
        command = [ f'{self.OpenScadPath}' ]

        # Tell OpenSCAD to automatically generate an STL file
        command.append(f'-o{outputFilePath}')

        # Add each variable setting parameter
        for parameter in parameters:
            # Retrieve the parameter value
            value = parameters[parameter]

            # If the value is a string, add escaped quotes around it
            if type(value) == str:
                value = f'"{value}"'

            command.append(f'-D{parameter}={value}')

        # Finally, specify the OpenSCAD source file
        command.append(inputFilePath)

        return command
