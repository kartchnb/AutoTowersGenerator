import os
import math

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger

from UM.Message import Message



class BedLevelController(QObject):
    _openScadFilename = 'bedlevel.scad'

    _presetTables = {
        'ender 3 (220x220)': {
            'filename': 'bedlevel ender 3 220x220.stl',
        },
    }



    def __init__(self, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__()

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._stlPath = stlPath

        self._pluginName = pluginName



    @staticmethod
    def getPresetNames()->list:
        return list(BedLevelController._presetTables.keys())



    def generate(self, preset='')->None:
        ''' Generate a bed level print - either preset or customized '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self.generateAutomatically()



    def _loadPreset(self, presetName)->None:
        ''' Load a preset bed level print '''
        # Load the preset table
        try:
            presetTable = self._presetTables[presetName]
        except KeyError:
            Logger.log('e', f'A BedLevel preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for BedLevel preset table "{presetName}" has not been defined')
            return

        # Warn if bed plate adhesion is selected

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the model name
        towerName = f'Preset BedLevel {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def generateAutomatically(self)->None:
        ''' This method automatically generates a bed level print customized to the current printer and settings '''

        # Query the current printer settings
        containerStack = Application.getInstance().getGlobalContainerStack()
        bed_adhesion = containerStack.getProperty('adhesion_type', 'value')
        print_width = containerStack.getProperty('machine_width', 'value')
        print_depth = containerStack.getProperty('machine_depth', 'value')
        line_width = containerStack.getProperty('line_width', 'value')
        layer_height = containerStack.getProperty('layer_height', 'value')

        # Warn if bed adhesion is selected
        if bed_adhesion != "none":
            Message(f'Bed adhesion is currently set to "{bed_adhesion}"\nSelect "none" for best results', title=self._pluginName).show()

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Print_Area_Width'] = print_width
        openScadParameters ['Print_Area_Depth'] = print_depth
        openScadParameters ['Line_Width'] = line_width
        openScadParameters ['Ring_Height'] = layer_height

        # Determine the print name
        printName = f'Auto-Generated BedLevel {print_width}x{print_depth}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(printName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the model
    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # In this case, there's no post-processing to be done, so just return the gcode unchanged
        return gcode;
