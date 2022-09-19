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

# Import the script that does the actual post-processing
from .scripts import RetractTower_PostProcessing



class RetractSpeedTowerController(QObject):
    _openScadFilename = 'retracttower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0

    _presetTables = {
        '10-50': {
            'filename': 'retractspeedtower-10-50.stl',
            'start value': 10,
            'change value': 10,
        },

        '35-75': {
            'filename': 'retractspeedtower-35-75.stl',
            'start value': 35,
            'change value': 10,
        },

        '60-100': {
            'filename': 'retractspeedtower-60-100.stl',
            'start value': 60,
            'change value': 10,
        },
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        QObject.__init__(self)

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._guiPath = guiPath
        self._stlPath = stlPath

        self._startSpeed = 0
        self._speedChange = 0
        self._baseLayers = 0
        self._sectionLayers = 0



    @staticmethod
    def getPresetNames()->list:
        return list(RetractSpeedTowerController._presetTables.keys())



    _cachedSettingsDialog = None

    @property
    def _settingsDialog(self)->QObject:
        ''' Lazy instantiation of this tower's settings dialog '''
        if self._cachedSettingsDialog is None:
            qmlFilePath = os.path.join(self._guiPath, 'RetractSpeedTowerDialog.qml')
            self._cachedSettingsDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedSettingsDialog



    # The starting retraction speed
    _startSpeedStr = '10'

    startSpeedStrChanged = pyqtSignal()

    def setStartSpeedStr(self, value)->None:
        self._startSpeedStr = value
        self.startSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startSpeedStrChanged, fset=setStartSpeedStr)
    def startSpeedStr(self)->str:
        return self._startSpeedStr



    # The ending retraction speed
    _endSpeedStr = '40'

    endSpeedStrChanged = pyqtSignal()

    def setEndSpeedStr(self, value)->None:
        self._endSpeedStr = value
        self.endSpeedStrChanged.emit()

    @pyqtProperty(str, notify=endSpeedStrChanged, fset=setEndSpeedStr)
    def endSpeedStr(self)->str:
        return self._endSpeedStr



    # The amount to change the retraction speed between tower sections
    _speedChangeStr = '10'

    speedChangeStrChanged = pyqtSignal()

    def setSpeedChange(self, value)->None:
        self._speedChangeStr = value
        self.speedChangeStrChanged.emit()

    @pyqtProperty(str, notify=speedChangeStrChanged, fset=setSpeedChange)
    def speedChangeStr(self)->str:
        return self._speedChangeStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = ''

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value)->None:
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self)->str:
        return self._towerDescriptionStr



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self._settingsDialog.show()



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetTables[presetName]
        except KeyError:
            Logger.log('e', f'A RetractSpeedTower preset named "{presetName}" was requested, but has not been correctly defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for RetractSpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's starting fan percent
        try:
            self._startSpeed = presetTable['start value']
        except KeyError:
            Logger.log('e', f'The "start value" for RetractSpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's fan change percent
        try:
            self._speedChange = presetTable['change value']
        except KeyError:
            Logger.log('e', f'The "change value" for RetractSpeedTower preset table "{presetName}" has not been defined')
            return

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Retraction Speed Tower {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    # This function is called when the 'Generate' button on the temp tower settings dialog is clicked
    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Determine the parameters for the tower
        startSpeed = float(self.startSpeedStr)
        endSpeed = float(self.endSpeedStr)
        speedChange = float(self.speedChangeStr)
        towerDescription = self.towerDescriptionStr

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty('layer_height', 'value')

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        baseHeight = self._baseLayers * layerHeight

        # Correct the section height to ensure an integer number of layers per section
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up
        sectionHeight = self._sectionLayers * layerHeight

        # Ensure the change amount has the correct sign
        if endSpeed >= startSpeed:
            speedChange = abs(speedChange)
        else:
            speedChange = -abs(speedChange)

        # Record the tower settings that will be needed for post-processing
        self._startSpeed = startSpeed
        self._speedChange = speedChange

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startSpeed
        openScadParameters ['Ending_Value'] = endSpeed
        openScadParameters ['Value_Change'] = speedChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        openScadParameters ['Column_Label'] = 'SPD'

        # Determine the tower name
        towerName = f'Auto-Generated Retraction Speed Tower {startSpeed}-{endSpeed}x{speedChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This code was modified from the RetractTower.py post-processing script
    # provided as part of 5axes' CalibrationShapes plugin
    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        # Determine the parameters for the tower
        startSpeed = float(self.startSpeedStr)
        speedChange = float(self.speedChangeStr)

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(gcode, self._startSpeed, self._speedChange, self._sectionLayers, self._baseLayers, 'speed')

        return gcode
