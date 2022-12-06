import os
import math

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSlot, pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import pyqtSlot, pyqtSignal, pyqtProperty

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger

from .ControllerBase import ControllerBase

# Import the script that does the actual post-processing
from ..Postprocessing import FanTower_PostProcessing



class FanTowerController(ControllerBase):
    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'FanTowerDialog.qml'

    _presetsTable = {
        'Fan Tower - Fan Speed 0-100': {
            'starting value': 0,
            'value change': 20,
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__("Fan Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable, pluginName)



    # The starting percentage value for the tower
    _startFanSpeedStr = '0'

    startFanSpeedStrChanged = pyqtSignal()
    
    def setstartFanSpeedStr(self, value)->None:
        self._startFanSpeedStr = value
        self.startFanSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startFanSpeedStrChanged, fset=setstartFanSpeedStr)
    def startFanSpeedStr(self)->str:
        return self._startFanSpeedStr



    # The ending percentage value for the tower
    _endFanSpeedStr = '100'

    endFanSpeedStrChanged = pyqtSignal()
    
    def setendFanSpeedStr(self, value)->None:
        self._endFanSpeedStr = value
        self.endFanSpeedStrChanged.emit()

    @pyqtProperty(str, notify=endFanSpeedStrChanged, fset=setendFanSpeedStr)
    def endFanSpeedStr(self)->str:
        return self._endFanSpeedStr



    # The amount to change the percentage between tower sections
    _fanSpeedChangeStr = '20'

    fanSpeedChangeStrChanged = pyqtSignal()
    
    def setfanSpeedChangeStr(self, value)->None:
        self._fanSpeedChangeStr = value
        self.fanSpeedChangeStrChanged.emit()

    @pyqtProperty(str, notify=fanSpeedChangeStrChanged, fset=setfanSpeedChangeStr)
    def fanSpeedChangeStr(self)->str:
        return self._fanSpeedChangeStr



    # The label to carve at the bottom of the tower
    _towerLabelStr = ''

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = 'FAN'

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value)->None:
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self)->str:
        return self._towerDescriptionStr



    # Determine if the same fan value is maintained while bridges are being printed
    _maintainBridgeValue = False

    maintainBridgeValueChanged = pyqtSignal()

    def setMaintainBridgeValue(self, value)->None:
        self._maintainBridgeValue = value
        self.maintainBridgeValueChanged.emit()

    @pyqtProperty(bool, notify=maintainBridgeValueChanged, fset=setMaintainBridgeValue)
    def maintainBridgeValue(self)->bool:
        return self._maintainBridgeValue



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''

        # Determine the STL file name
        stlFileName = f'{presetName}.stl'
        stlFilePath = self._getStlFilePath(stlFileName)

        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A Fan Tower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset values
        try:
            self._startFanSpeed = presetTable['starting value']
            self._fanSpeedChange = presetTable['value change']
        except KeyError as e:
            Logger.log('e', f'The "{e.args[0]}" entry does not exit for the Fan Tower preset "{presetName}"')
            return

        # Use the nominal base and section heights for this preset tower
        self._baseHeight = self._nominalBaseHeight
        self._sectionHeight = self._nominalSectionHeight

        # Determine the tower name
        towerName = f'Preset {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Determine the parameters for the tower
        startFanSpeed = float(self.startFanSpeedStr)
        endFanSpeed = float(self.endFanSpeedStr)
        fanSpeedChange = float(self.fanSpeedChangeStr)
        towerLabel = self.towerLabelStr
        towerDescription = self.towerDescriptionStr

        # Ensure the fan speed change value has the correct sign
        fanSpeedChange = self._correctChangeValueSign(fanSpeedChange, startFanSpeed, endFanSpeed)

        # Calculate the optimal base and section height, given the current printing layer height
        baseHeight = self._calculateOptimalHeight(self._nominalBaseHeight)
        sectionHeight = self._calculateOptimalHeight(self._nominalSectionHeight)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startFanSpeed
        openScadParameters ['Ending_Value'] = endFanSpeed
        openScadParameters ['Value_Change'] = fanSpeedChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Record the tower settings that will be needed for post-processing
        self._startFanSpeed = startFanSpeed
        self._fanSpeedChange = fanSpeedChange
        self._baseHeight = baseHeight
        self._sectionHeight = sectionHeight

        # Determine the tower name
        towerName = f'Custom Fan Tower - Fan Speed {startFanSpeed}-{endFanSpeed}x{fanSpeedChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # Call the post-processing script
        gcode = FanTower_PostProcessing.execute(
            gcode, 
            self._baseHeight, 
            self._sectionHeight, 
            self._initialLayerHeight,
            self._layerHeight, 
            self._startFanSpeed, 
            self._fanSpeedChange, 
            self.maintainBridgeValue, 
            enable_lcd_messages
            )

        return gcode
