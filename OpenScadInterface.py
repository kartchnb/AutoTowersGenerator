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

        # Determine the Operating system being used
        self._system = platform.system().lower()



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

        # Initialize the command line
        command_line = ''

        # If running on Linux, the AppImage messes with the LD_LIBRARY_PATH environmental variable
        # In order for OpenScad to run correctly, this variable needs to be unset
        # At least, on my machine...
        if self._system == 'linux':
            command_line += f'unset LD_LIBRARY_PATH; '

        # Add the OpenSCAD command
        command_line += f'"{openScadPath}"'

        # Tell OpenSCAD to automatically generate an STL file
        command_line += f' -o {outputFilePath}'

        # Add each variable setting parameter
        for parameter in parameters:
            # Retrieve the parameter value
            value = parameters[parameter]

            # If the value is a string, add quotes around it
            if type(value) == str:
                value = f'\\"{value}\\"'

            command_line += f' -D "{parameter}={value}"'

        # Finally, specify the OpenSCAD source file
        command_line += f' "{inputFilePath}"'

        return command_line



    _defaultOpenScadPath = ''

    @property
    def DefaultOpenScadPath(self):
        if self._defaultOpenScadPath == '':
            # On Linux, check for openscad in the current path
            if self._system == "linux":
                # If the 'which' command can find the openscad path, use the path directly
                command = 'which openscad'
                which_result = subprocess.run(command, capture_output=True, text=True, shell=True).stdout.strip()
                if which_result != '':
                    self._defaultOpenScadPath = which_result

            # This path for Macintosh was borrowed from Thopiekar's OpenSCAD Integration plugin (https://thopiekar.eu/cura/cad/openscad)
            # I have no way of verifying it works...
            if self._system == 'darwin':
                self._defaultOpenScadPath = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

            # For Windows, OpenSCAD should be installed in the Program Files folder
            elif self._system == 'windows':
                program_files_path = f'{os.path.join(os.getenv("PROGRAMFILES"), "OpenSCAD", "openscad.exe")}'
                if os.path.isfile(program_files_path):
                    self._defaultOpenScadPath = program_files_path

            # Cura shouldn't be running on any other platform, but try a sensible default
            else:
                self._defaultOpenScadPath = 'openscad'
                
        return self._defaultOpenScadPath
