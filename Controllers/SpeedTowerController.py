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

from .ControllerBase import ControllerBase

# Import the scripts that do the actual post-processing
from ..Postprocessing import TravelSpeedTower_PostProcessing
from ..Postprocessing import MiscSpeedTower_PostProcessing



class SpeedTowerController(ControllerBase):
    _openScadFilename = 'speedtower.scad'
    _qmlFilename = 'SpeedTowerDialog.qml'

    _presetsTable = {
        'Travel Speed 20-100': {
            'filename': 'speedtower travel speed 20-100.stl',
            'start value': 20,
            'change value': 20,
            'tower type': 'Travel Speed'
        },

        'Travel Speed 50-150': {
            'filename': 'speedtower travel speed 50-150.stl',
            'start value': 50,
            'change value': 20,
            'tower type': 'Travel Speed'
        },

        'Travel Speed 100-200': {
            'filename': 'speedtower travel speed 100-200.stl',
            'start value': 100,
            'change value': 20,
            'tower type': 'Travel Speed'
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': False,
        'layer_height': None,
        'support_enable': False,
    }

    _towerTypesModel = [
        {'value': 'Travel Speed', 'label': 'TRAVEL SPEED'}, 
        {'value': 'Acceleration', 'label': 'ACCELERATION'}, 
        {'value': 'Jerk', 'label': 'JERK'}, 
        {'value': 'Junction', 'label': 'JUNCTION'}, 
        {'value': 'Marlin Linear', 'label': 'MARLIN LINEAR'}, 
        {'value': 'RepRap Pressure', 'label': 'REPRAP PRESSURE'},
    ]

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__("Speed Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable)



    # The available tower types
    @pyqtProperty(list)
    def towerTypesModel(self):
        return self._towerTypesModel



    # The speed tower type 
    _towerType = _towerTypesModel[0]['value']

    towerTypeChanged = pyqtSignal()

    def setTowerType(self, value)->None:
        self._towerType = value
        self.towerTypeChanged.emit()

    @pyqtProperty(str, notify=towerTypeChanged, fset=setTowerType)
    def towerType(self)->str:
        return self._towerType



    # The starting speed value for the tower
    _startSpeedStr = '20'

    startSpeedStrChanged = pyqtSignal()
    
    def setStartSpeedStr(self, value)->None:
        self._startSpeedStr = value
        self.startSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startSpeedStrChanged, fset=setStartSpeedStr)
    def startSpeedStr(self)->str:
        return self._startSpeedStr



    # The ending speed value for the tower
    _endSpeedStr = '100'

    endSpeedStrChanged = pyqtSignal()
    
    def setEndSpeedStr(self, value)->None:
        self._endSpeedStr = value
        self.endSpeedStrChanged.emit()

    @pyqtProperty(str, notify=endSpeedStrChanged, fset=setEndSpeedStr)
    def endSpeedStr(self)->str:
        return self._endSpeedStr



    # The amount to change the speed between tower sections
    _speedChangeStr = '20'

    speedChangeStrChanged = pyqtSignal()
    
    def setSpeedChangeStr(self, value)->None:
        self._speedChangeStr = value
        self.speedChangeStrChanged.emit()

    @pyqtProperty(str, notify=speedChangeStrChanged, fset=setSpeedChangeStr)
    def speedChangeStr(self)->str:
        return self._speedChangeStr



    # The label to add to the tower
    _towerLabelStr = _towerTypesModel[0]['label']

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The temperature label to add to the tower
    _temperatureLabelStr = ''

    temperatureLabelStrChanged = pyqtSignal()
    
    def setTemperatureLabelStr(self, value)->None:
        self._temperatureLabelStr = value
        self.temperatureLabelStrChanged.emit()

    @pyqtProperty(str, notify=temperatureLabelStrChanged, fset=setTemperatureLabelStr)
    def temperatureLabelStr(self)->str:
        return self._temperatureLabelStr



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A SpeedTower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's starting speed
        try:
            self._startValue = presetTable['start value']
        except KeyError:
            Logger.log('e', f'The "start value" for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's speed change value
        try:
            self._valueChange = presetTable['change value']
        except KeyError:
            Logger.log('e', f'The "change value" for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's tower type value
        try:
            self._towerType = presetTable['tower type']
        except KeyError:
            Logger.log('e', f'The "tower type" for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Speed Tower ({self._towerType}) {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Read the parameters directly from the dialog
        startSpeed = float(self.startSpeedStr)
        endSpeed = float(self.endSpeedStr)
        speedChange = float(self.speedChangeStr)
        towerLabel = self.towerLabelStr
        temperatureLabel = self.temperatureLabelStr

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
        self._startValue = startSpeed
        self._valueChange = speedChange

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startSpeed
        openScadParameters ['Ending_Value'] = endSpeed
        openScadParameters ['Value_Change'] = speedChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerLabel
        openScadParameters ['Temperature_Label'] = temperatureLabel

        # Determine the tower name
        towerName = f'Auto-Generated Speed Tower ({self._towerType}) {startSpeed}-{endSpeed}x{speedChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        if self._towerType == 'Travel Speed':
            # Query the current print speed
            currentPrintSpeed = Application.getInstance().getGlobalContainerStack().getProperty('speed_print', 'value')
            gcode = TravelSpeedTower_PostProcessing.execute(gcode, self._startValue, self._valueChange, self._sectionLayers, self._baseLayers, currentPrintSpeed)
        else:
            gcode = MiscSpeedTower_PostProcessing.execute(gcode, self._startValue, self._valueChange, self._sectionLayers, self._baseLayers, self._towerType)

        return gcode
