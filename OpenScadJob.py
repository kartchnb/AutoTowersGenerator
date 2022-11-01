import os
import shutil
import tempfile

from UM.Job import Job

from . import OpenScadInterface



class OpenScadJob(Job):
    '''A simple class used to generate an STL file using OpenSCAD
    
    Since this can be a lengthy process, Uranium's Job class is used
    to perform the work in the background'''

    def __init__(self, openScadInterface, openScadFilePath, openScadParameters, stlFilePath):
        super().__init__()
        self._openScadInterface = openScadInterface
        self._openScadFilePath = openScadFilePath
        self._openScadParameters = openScadParameters
        self._stlFilePath = stlFilePath



    def run(self) -> None:
        '''Generate an STL from an OpenSCAD file'''

        # Check if the openscad file is in a symbolically-linked directory
        # OpenScad apparently can't handle source files in symbolically-linked directories (at least on Windows)
        openScadFileDir = os.path.dirname(self._openScadFilePath)
        if os.path.islink(openScadFileDir):

            # Copy the file to the system's temporary directory
            openScadFileName = os.path.basename(self._openScadFilePath)
            tempDir = tempfile.gettempdir()
            tempOpenScadFilePath = os.path.join(tempDir, openScadFileName)
            shutil.copy2(self._openScadFilePath, tempOpenScadFilePath)

            # Run openscad with the temporary file
            self._openScadInterface.GenerateStl(tempOpenScadFilePath, self._openScadParameters, self._stlFilePath)

            # Delete the temporary file
            os.remove(tempOpenScadFilePath)

        # If this is just a normal, everyday file, run openscad normally
        else:
            self._openScadInterface.GenerateStl(self._openScadFilePath, self._openScadParameters, self._stlFilePath)
