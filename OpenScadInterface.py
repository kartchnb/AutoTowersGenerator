import os
import platform
from shutil import which
import subprocess

from UM.Logger import Logger
from UM.Message import Message



class OpenScadInterface:
    openScadPath = ''



    def __init__(self, pluginName):
        self.errorMessage = ''
        self._openScadPath = ''
        self._pluginName = pluginName



    def SetOpenScadPath(self, openScadPath):
        ''' Manually assign the OpenScad path '''

        self._openScadPath = openScadPath



    @property
    def OpenScadPath(self)->str:
        ''' Return the path to OpenScad - an attempt will be made to automatically determine it if needed '''
        if self._openScadPath == '':
            self._openScadPath = self._GetDefaultOpenScadPath()

        return self._openScadPath



    @property
    def OpenScadPathValid(self)->bool:
        ''' Return true if the OpenScad path is valid '''

        # Attempt to verify the OpenScad executable is valid by querying the OpenScad version number
        command = f'{self._OpenScadCommand} -v'
        response = subprocess.run(command, capture_output=True, text=True, shell=True).stderr.strip()
        valid = 'OpenSCAD version' in response

        return valid



    @property
    def _OpenScadCommand(self)->str:
        ''' Converts the OpenScad path into a form that can be executed
            Currently, this is only needed for Linux '''

        command = ''

        # This only makes sense if the OpenScad path has been determined or set
        if self.OpenScadPath != '':

            # If running on Linux as an AppImage, the LD_LIBRARY_PATH environmental variable can cause issues
            # In order for OpenScad to run correctly in this case, LD_LIBRARY_PATH needs to be unset
            # At least on my machine...
            system = platform.system().lower()
            if system == 'linux':

                # Prefix the OpenScad call with a command to unset LD_LIBRARY_PATH
                command += 'unset LD_LIBRARY_PATH; '

            # Add the executable to the command
            # Quotes are added in case there are embedded spaces
            command += f'"{self.OpenScadPath}"'

        return command



    def GenerateStl(self, inputFilePath, parameters, outputFilePath):
        '''Execute an OpenSCAD file with the given parameters to generate a model'''

        # If the OpenScad path is valid
        if self.OpenScadPathValid:
            # Build the OpenSCAD command
            command = self._GenerateOpenScadCommand(inputFilePath, parameters, outputFilePath)
            Logger.log('d', f'Executing OpenSCAD command: {command}')

            # Execute the OpenSCAD command and capture the error output
            # Output in stderr does not necessarily indicate an error - OpenSCAD seems to routinely output to stderr
            try:
                self.commandResult = subprocess.run(command, capture_output=True, text=True, shell=True).stderr.strip()

            except FileNotFoundError:
                Message(f'OpenSCAD was not found at path "{self._openScadPath}"', title=self._pluginName, message_type=Message.MessageType.ERROR).show()

        # If the OpenScad path is invalid
        else:
            Message(f'The OpenSCAD path is invalid', title=self._pluginName, message_type=Message.MessageType.ERROR).show()



    def _GenerateOpenScadCommand(self, inputFilePath, parameters, outputFilePath):
        '''Generate an OpenSCAD command from an input file path, parameters, and output file path'''

        # Start the command line
        command_line = self._OpenScadCommand

        # Tell OpenSCAD to automatically generate an STL file
        command_line += f' -o "{outputFilePath}"'

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



    def _GetDefaultOpenScadPath(self):
        ''' Attempt to determine the default location of the OpenScad executable '''

        # This makes a sensible default
        openScadPath = 'openscad'

        # Determine the system that Cura is being run on
        system = platform.system().lower()

        # On Linux, check for openscad in the current path
        if system == "linux":
            # If the 'which' command can find the openscad path, use the path directly
            command = 'which openscad'
            which_result = subprocess.run(command, capture_output=True, text=True, shell=True).stdout.strip()
            if which_result != '':
                openScadPath = which_result

        # This path for Macintosh was borrowed from Thopiekar's OpenSCAD Integration plugin (https://thopiekar.eu/cura/cad/openscad)
        # I have no way of verifying it works...
        if system == 'darwin':
            openScadPath = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

        # For Windows, OpenSCAD should be installed in the Program Files folder
        elif system == 'windows':
            program_files_path = f'{os.path.join(os.getenv("PROGRAMFILES"), "OpenSCAD", "openscad.exe")}'
            if os.path.isfile(program_files_path):
                openScadPath = program_files_path

        return openScadPath
