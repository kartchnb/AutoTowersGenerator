import glob
import os
import platform
from shutil import which
import subprocess

from UM.Logger import Logger
from UM.Message import Message



class OpenScadInterface:
    openScadPath = ''



    def __init__(self):
        self.errorMessage = ''



    def GenerateStl(self, inputFilePath, parameters, outputFilePath, openScadPath = ''):
        '''Execute an OpenSCAD file with the given parameters to generate a model'''

        # Build the OpenSCAD command
        command = self.GenerateOpenScadCommand(inputFilePath, parameters, outputFilePath, openScadPath)
        Logger.log('d', f'Executing OpenSCAD command: {command}')

        # Execute the OpenSCAD command and capture the error output
        # Output in stderr does not necessarily indicate an error - OpenSCAD seems to routinely output to stderr
        try:
            self.errorMessage = subprocess.run(command, capture_output=True, text=True, shell=True).stderr.strip()
        except FileNotFoundError:
            self.errorMessage = f'OpenSCAD not found at path "{openScadPath}"'



    def GenerateOpenScadCommand(self, inputFilePath, parameters, outputFilePath, openScadPath = ''):
        '''Generate an OpenSCAD command from an input file path, parameters, and output file path'''

        # If the OpenSCAD path was not supplied, use the default path
        if openScadPath == '':
            openScadPath = self.DefaultOpenScadPath

        # Start the command array with the OpenSCAD command
        command = f'"{openScadPath}"'

        # Tell OpenSCAD to automatically generate an STL file
        command += f' -o {outputFilePath}'

        # Add each variable setting parameter
        for parameter in parameters:
            # Retrieve the parameter value
            value = parameters[parameter]

            # If the value is a string, add quotes around it
            if type(value) == str:
                value = f'\\"{value}\\"'

            command += f' -D "{parameter}={value}"'

        # Finally, specify the OpenSCAD source file
        command += f' "{inputFilePath}"'

        return command



    _defaultOpenScadPath = ''

    @property
    def DefaultOpenScadPath(self):
        if self._defaultOpenScadPath == '':
            # Determine the Operating system being used
            system = platform.system()

            # On Linux, check for openscad in the current path
            if system.lower() == "linux":
                # If the 'which' command can find the openscad path, use the path directly
                command = 'which openscad'
                which_result = subprocess.run(command, capture_output=True, text=True, shell=True).stdout.strip()
                if which_result != '':
                    self._defaultOpenScadPath = which_result

            # This path for Macintosh was borrowed from Thopiekar's OpenSCAD Integration plugin (https://thopiekar.eu/cura/cad/openscad)
            # I have no way of verifying it works...
            if system.lower() == 'darwin':
                self._defaultOpenScadPath = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

            # For Windows, OpenSCAD should be installed in the Program Files folder
            elif system == 'Windows':
                program_files_path = f'{os.path.join(os.getenv("PROGRAMFILES"), "OpenSCAD", "openscad.exe")}'
                if os.path.isfile(program_files_path):
                    self._defaultOpenScadPath = program_files_path
                
        return self._defaultOpenScadPath
