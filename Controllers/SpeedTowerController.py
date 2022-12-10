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
from ..Postprocessing import PrintSpeedTower_PostProcessing
from ..Postprocessing import MiscSpeedTower_PostProcessing



class SpeedTowerController(ControllerBase):
    _openScadFilename = 'speedtower.scad'
    _qmlFilename = 'SpeedTowerDialog.qml'

    _presetsTable = {
        'Speed Tower - Print Speed 20-100': {
            'starting value': 20,
            'value change': 20,
            'tower type': 'Print Speed',
        },

        'Speed Tower - Print Speed 50-150': {
            'starting value': 50,
            'value change': 20,
            'tower type': 'Print Speed',
        },

        'Speed Tower - Print Speed 100-200': {
            'starting value': 100,
            'value change': 20,
            'tower type': 'Print Speed',
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }

    _towerTypesModel = [
        {'value': 'Print Speed', 'label': 'PRINT SPEED'}, 
        {'value': 'Acceleration', 'label': 'ACCELERATION'}, 
        {'value': 'Jerk', 'label': 'JERK'}, 
        {'value': 'Junction', 'label': 'JUNCTION'}, 
        {'value': 'Marlin Linear', 'label': 'MARLIN LINEAR'}, 
        {'value': 'RepRap Pressure', 'label': 'REPRAP PRESSURE'},
    ]



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__("Speed Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable, pluginName)



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



    # The length of each of the tower wings
    _wingLengthStr = '50'

    wingLengthStrChanged = pyqtSignal()

    def setWingLengthStr(self, value)->None:
        self._wingLengthStr = value
        self.wingLengthStrChanged.emit()

    @pyqtProperty(str, notify=wingLengthStrChanged, fset=setWingLengthStr)
    def wingLengthStr(self)->str:
        return self._wingLengthStr



    # The label to add to the tower
    _towerLabelStr = _towerTypesModel[0]['label']

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The a description to add to the tower
    _descriptionLabelStr = ''

    descriptionLabelStrChanged = pyqtSignal()
    
    def setDescriptionLabelStr(self, value)->None:
        self._descriptionLabelStr = value
        self.descriptionLabelStrChanged.emit()

    @pyqtProperty(str, notify=descriptionLabelStrChanged, fset=setDescriptionLabelStr)
    def descriptionLabelStr(self)->str:
        return self._descriptionLabelStr



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''

        # Determine the STL file name
        stlFileName = f'{presetName}.stl'
        stlFilePath = self._getStlFilePath(stlFileName)

        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A SpeedTower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset values
        try:
            self._startValue = presetTable['starting value']
            self._valueChange = presetTable['value change']
            self._towerType = presetTable['tower type']
        except KeyError as e:
            Logger.log('e', f'The "{e.args[0]}" entry does not exit for the FanTower preset "{presetName}"')
            return

        # Use the nominal base and section heights for this preset tower
        self._baseHeight = self._nominalBaseHeight
        self._sectionHeight = self._nominalSectionHeight

        # Determine the tower name
        towerName = f'Custom {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Determine the parameters for the tower
        startSpeed = float(self.startSpeedStr)
        endSpeed = float(self.endSpeedStr)
        speedChange = float(self.speedChangeStr)
        wingLength = float(self.wingLengthStr)
        towerLabel = self.towerLabelStr
        descriptionLabel = self.descriptionLabelStr

        # Ensure the change amount has the correct sign
        speedChange = self._correctChangeValueSign(speedChange, startSpeed, endSpeed)

        # Calculate the optimal base and section height, given the current printing layer height
        baseHeight = self._calculateOptimalHeight(self._nominalBaseHeight)
        sectionHeight = self._calculateOptimalHeight(self._nominalSectionHeight)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Speed_Value'] = startSpeed
        openScadParameters ['Ending_Speed_Value'] = endSpeed
        openScadParameters ['Speed_Value_Change'] = speedChange
        openScadParameters ['Wing_Length'] = wingLength
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerLabel
        openScadParameters ['Tower_Description'] = descriptionLabel

        # Record the tower settings that will be needed for post-processing
        self._startValue = startSpeed
        self._valueChange = speedChange
        self._baseHeight = baseHeight
        self._sectionHeight = sectionHeight

        # Determine the tower name
        towerName = f'Custom Speed Tower - {self._towerType} {startSpeed}-{endSpeed}x{speedChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script for print speed towers
        if self._towerType == 'Print Speed':
            gcode = PrintSpeedTower_PostProcessing.execute(
                gcode, 
                self._baseHeight, 
                self._sectionHeight, 
                self._initialLayerHeight, 
                self._layerHeight, 
                self._startValue, 
                self._valueChange, 
                self._printSpeed,
                enable_lcd_messages
                )
        
        # Call the post-processing script for non print speed towers
        else:
            gcode = MiscSpeedTower_PostProcessing.execute(
                gcode, 
                self._baseHeight, 
                self._sectionHeight, 
                self._initialLayerHeight, 
                self._layerHeight, 
                self._startValue, 
                self._valueChange, 
                self._towerType, 
                enable_lcd_messages
                )

        return gcode
