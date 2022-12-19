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

# Import the script that does the actual post-processing
from ..Postprocessing import TempTower_PostProcessing



class TempTowerController(ControllerBase):
    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'TempTowerDialog.qml'

    _presetsTable = {
        'Temperature Tower - ABA': {
            'starting value': 260,
            'value change': -5,
        },

        'Temperature Tower - ABS': {
            'starting value': 250,
            'value change': -5,
        },

        'Temperature Tower - Nylon': {
            'starting value': 260,
            'value change': -5,
        },

        'Temperature Tower - PC': {
            'starting value': 310,
            'value change': -5,
        },

        'Temperature Tower - PETG': {
            'starting value': 250,
            'value change': -5,
        },

        'Temperature Tower - PLA': {
            'starting value': 230,
            'value change': -5,
        },

        'Temperature Tower - PLA+': {
            'starting value': 230,
            'value change': -5,
        },

        'Temperature Tower - TPU': {
            'starting value': 230,
            'value change': -5,
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__("Temp Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable, pluginName)



    # The starting temperature value for the tower
    _startTemperatureStr = '220'

    startTemperatureStrChanged = pyqtSignal()
    
    def setStartTemperatureStr(self, value)->None:
        self._startTemperatureStr = value
        self.startTemperatureStrChanged.emit()

    @pyqtProperty(str, notify=startTemperatureStrChanged, fset=setStartTemperatureStr)
    def startTemperatureStr(self)->str:
        return self._startTemperatureStr



    # The ending temperature value for the tower
    _endTemperatureStr = '180'

    endTemperatureStrChanged = pyqtSignal()
    
    def setEndTemperatureStr(self, value)->None:
        self._endTemperatureStr = value
        self.endTemperatureStrChanged.emit()

    @pyqtProperty(str, notify=endTemperatureStrChanged, fset=setEndTemperatureStr)
    def endTemperatureStr(self)->str:
        return self._endTemperatureStr



    # The amount to change the temperature between tower sections
    _temperatureChangeStr = '-5'

    temperatureChangeStrChanged = pyqtSignal()
    
    def setTemperatureChangeStr(self, value)->None:
        self._temperatureChangeStr = value
        self.temperatureChangeStrChanged.emit()

    @pyqtProperty(str, notify=temperatureChangeStrChanged, fset=setTemperatureChangeStr)
    def temperatureChangeStr(self)->str:
        return self._temperatureChangeStr



    # The material label to add to the tower
    _towerLabelStr = ''

    towerLabelStrChanged = pyqtSignal()
    
    def setMaterialLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setMaterialLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = 'TEMP'

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value)->None:
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self)->str:
        return self._towerDescriptionStr



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''

        # Determine the STL file name
        stlFileName = f'{presetName}.stl'
        stlFilePath = self._getStlFilePath(stlFileName)

        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A Temp Tower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset values
        try:
            self._startTemperature = presetTable['starting value']
            self._temperatureChange = presetTable['value change']
        except KeyError as e:
            Logger.log('e', f'The "{e.args[0]}" entry does not exit for the Temp Tower preset "{presetName}"')
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
        # Read the parameters directly from the dialog
        startTemperature = float(self.startTemperatureStr)
        endTemperature = float(self.endTemperatureStr)
        temperatureChange = float(self.temperatureChangeStr)
        towerLabel = self.towerLabelStr
        towerDescription = self.towerDescriptionStr

        # Ensure the change amount has the correct sign
        temperatureChange = self._correctChangeValueSign(temperatureChange, startTemperature, endTemperature)

        # Calculate the optimal base and section height, given the current printing layer height
        baseHeight = self._calculateOptimalHeight(self._nominalBaseHeight)
        sectionHeight = self._calculateOptimalHeight(self._nominalSectionHeight)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startTemperature
        openScadParameters ['Ending_Value'] = endTemperature
        openScadParameters ['Value_Change'] = temperatureChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Record the tower settings that will be needed for post-processing
        self._startTemperature = startTemperature
        self._temperatureChange = temperatureChange
        self._baseHeight = baseHeight
        self._sectionHeight = sectionHeight

        # Determine the tower name
        towerName = f'Custom Temp Tower - {startTemperature}-{endTemperature}x{temperatureChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        gcode = TempTower_PostProcessing.execute(
            gcode, 
            self._baseHeight, 
            self._sectionHeight, 
            self._initialLayerHeight,
            self._layerHeight, 
            self._startTemperature, 
            self._temperatureChange, 
            enable_lcd_messages
            )

        return gcode
