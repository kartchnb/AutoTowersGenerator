import os
import platform
import shutil
import subprocess
import tempfile

from UM.Logger import Logger
from UM.Message import Message



class OpenScadInterface:
    _openscad_version_id = 'OpenSCAD version '



    def __init__(self, pluginName):
        self.errorMessage = ''
        self._openScadPath = ''
        self._pluginName = pluginName
        self._openscad_version = ''



    def SetOpenScadPath(self, openScadPath):
        ''' Manually assign the OpenScad path '''

        self._openScadPath = openScadPath



    @property
    def OpenScadVersion(self):
        return self._openscad_version



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
        Logger.log('d', f'Checking for OpenSCAD returned the following response: "{response}"')

        # OpenScad is considered valid if it returns a response including the string 'OpenScad version'
        valid = self._openscad_version_id in response
        if valid:
            self._openscad_version = response.replace(self._openscad_version_id, '')
            Logger.log('d', 'The OpenSCAD path is valid')
        else:
            self._openscad_version = ''
            Logger.log('d', 'The OpenSCAD path is not valid')

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

            path = self.OpenScadPath

            # Add the executable to the command
            # Quotes are added in case there are embedded spaces in the path, but we shouldn't double up if already quoted
            command += f'"{path}"' if not path.startswith('\"') else path

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
        inputFilePath = self._SymLinkWorkAround(inputFilePath)
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

        # For Windows, OpenSCAD should be installed in one of the Program Files folder
        elif system == 'windows':
            program_files_paths = (
                os.getenv("PROGRAMFILES"),
                os.getenv("PROGRAMFILES(X86)")
            )
            for program_files_path in program_files_paths:
                testPath = os.path.join(program_files_path, "OpenSCAD", "openscad.exe")
                if os.path.isfile(testPath):
                    openScadPath = testPath
                    break

        return openScadPath



    def _SymLinkWorkAround(self, filePath)->str:
        ''' OpenSCAD does not appear to handle files with a symlink directory anywhere in its path
          This method checks for this condition and copies the provided file to a temprary location, if needed
          The original path is returned if a symlink is involved, otherwise the path to the temporary file is returned '''
        returnPath = filePath

        # Determine if any element in the file path is a symlink
        pathCopy = os.path.normpath(filePath)
        isSymLink = False
        while True:
            # Check if the current portion of the path is a sym link
            if os.path.islink(pathCopy):
                isSymLink = True
                break

            # Throw away the last portion of the path and check again
            split = os.path.split(pathCopy)
            if pathCopy == split[0]:
                break
            pathCopy = split[0]

        # If the file path involves a sym link, copy it to a temporary file
        if isSymLink:
            # Copy the file to the system's temporary directory
            fileName = os.path.basename(filePath)
            tempDir = tempfile.gettempdir()
            tempFilePath = os.path.join(tempDir, fileName)
            shutil.copy2(filePath, tempFilePath)
            returnPath = tempFilePath

        return returnPath
