from UM.Job import Job

from . import OpenScadInterface



class OpenScadJob(Job):
    '''A simple class used to generate an STL file using OpenSCAD
    
    Since this can be a lengthy process, Uranium's Job class is used
    to perform the work in the background'''

    def __init__(self, openScadInterface, openScadFilePath, openScadParameters, stlFilePath, openScadPath):
        super().__init__()
        self._openScadInterface = openScadInterface
        self._openScadFilePath = openScadFilePath
        self._openScadParameters = openScadParameters
        self._stlFilePath = stlFilePath
        self._openScadPath = openScadPath



    def run(self) -> None:
        '''Generate an STL from an OpenSCAD file'''
        self._openScadInterface.GenerateStl(self._openScadFilePath, self._openScadParameters, self._stlFilePath, self._openScadPath)
