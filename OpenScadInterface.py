import glob
import os
import platform
import subprocess

from UM.Logger import Logger
from UM.Message import Message



class OpenScadInterface:
    OpenScadPath = None



    def __init__(self):
        # Determine the default path of the OpenSCAD command

        system = platform.system()
        Logger.log('d', f'Platform is reported as "{system}"')

        # For Linux, OpenSCAD should be in the default path
        if system == 'Linux':
            self.OpenScadPath = 'openscad'

        # This path for macs was stolen from Thopiekar's OpenSCAD Integration plugin (https://thopiekar.eu/cura/cad/openscad)
        # I have no way of verifying this, though...
        elif system == 'Darwin':
            self.OpenScadPath = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'

        # For Windows, OpenSCAD should be installed in the Program Files folder
        elif system == 'Windows':
            program_files_path = os.path.join(os.getenv('PROGRAMFILES'), 'OpenSCAD', 'openscad.exe')
            program_files_x86_path = os.path.join(os.getenv('PROGRAMFILES(X86)'), 'OpenSCAD', 'openscad.exe')
            if os.path.is_file(program_files_path):
                self.OpenScadPath = program_files_path
            elif os.path.is_file(program_files_x86_path):
                self.OpenScadPath = program_files_x86_path
            else:
                Message('Failed to locate OpenSCAD installed in the Program Files directories\nPlease ensure OpenSCAD is installed correctly or change its path in the AutoTowers settings menu', title='AutoTowers').show()

        # If none of the above apply, try a default that might work
        else:
            self.OpenScadPath = 'openscad'

        Logger.log('d', f'OpenSCAD path is set to "{self.OpenScadPath}"')



    def GenerateStl(self, inputFilePath, parameters, outputFilePath):
        # Start the command array with the OpenSCAD command
        command = [self.OpenScadPath]

        # Tell OpenSCAD to automatically generate an STL file
        command.append(f'-o{outputFilePath}')

        # Add each variable setting parameter
        for parameter in parameters:
            # Retrieve the parameter value
            value = parameters[parameter]

            # If the value is a string, add escaped quotes around it
            if type(value) == str:
                value = f'\"{value}\"'

            command.append(f'-D{parameter}={value}')

        # Finally, specify the OpenSCAD source file
        command.append(inputFilePath)

        # Execute the command
        subprocess.run(command)
