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



class BedLevelPrintController(QObject):
    _openScadFilename = 'bedlevelprint.scad'

    _presetTables = {
        '220x220': {
            'filename': 'bedlevel 220x220.stl',
            'print area width': 220,
            'print area depth': 220,
        },
    }


    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__()

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._stlPath = stlPath



    @staticmethod
    def getPresetNames()->list:
        return list(BedLevelPrintController._presetTables.keys())



    def settingsAreCompatible(self)->str:
        ''' Check whether Cura's settings are compatible with this tower '''

        containerStack = Application.getInstance().getGlobalContainerStack()

        # The tower cannot be generated if supports are enabled
        adhesion_setting = containerStack.getProperty('adhesion_type', 'value')
        if adhesion_setting != 'none':
            setting_label = containerStack.getProperty('adhesion_type', 'label')
            return f'The Cura setting "{setting_label}" must be set to "none" to print a bed level print.'

        return ''



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self._generateCustom()



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
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

        # Load the preset's starting fan percent
        try:
            self._startPercent = presetTable['print area width']
        except KeyError:
            Logger.log('e', f'The "print area width" for BedLevel preset table "{presetName}" has not been defined')
            return

        # Load the preset's fan change percent
        try:
            self._percentChange = presetTable['print area depth']
        except KeyError:
            Logger.log('e', f'The "print area depth" for BedLevel preset table "{presetName}" has not been defined')
            return

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Bed Level Print {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    def _generateCustom(self)->None:
        ''' Generates a bed level print based on the current print area and Cura settings '''

        containerStack = Application.getInstance().getGlobalContainerStack()

        # Query the bed size
        bed_width = containerStack.getProperty('machine_width', 'value')
        bed_depth = containerStack.getProperty('machine_depth', 'value')

        # Query the current layer height
        layer_height = containerStack.getProperty("layer_height", "value")

        # Query the current line width
        line_width = containerStack.getProperty('line_width', 'value')

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Print_Area_Width'] = bed_width
        openScadParameters ['Print_Area_Depth'] = bed_depth
        openScadParameters ['Line_Width'] = line_width
        openScadParameters ['Line_Height'] = layer_height

        # Determine the tower name
        towerName = f'Auto-Generated Bed Level Print {bed_width}x{bed_depth}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # No post-processing needs to be done for this print
        return gcode
