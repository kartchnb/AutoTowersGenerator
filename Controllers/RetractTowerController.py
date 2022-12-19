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
from ..Postprocessing import RetractTower_PostProcessing



class RetractTowerController(ControllerBase):
    _openScadFilename = 'retracttower.scad'
    _qmlFilename = 'RetractTowerDialog.qml'

    _presetsTable = {
        'Retract Tower - Retract Distance 1-6': {
            'starting value': 1,
            'value change': 1,
            'tower type': 'Distance',
       },

        'Retract Tower - Retract Distance 4-9': {
            'starting value': 4,
            'value change': 1,
            'tower type': 'Distance',
        },

        'Retract Tower - Retract Distance 7-12': {
            'starting value': 7,
            'value change': 1,
            'tower type': 'Distance',
        },
 
        'Retract Tower - Retract Speed 10-50': {
            'starting value': 10,
            'value change': 10,
            'tower type': 'Speed',
        },

        'Retract Tower - Retract Speed 35-75': {
            'starting value': 35,
            'value change': 10,
            'tower type': 'Speed',
        },

        'Retract Tower - Retract Speed 60-100': {
            'starting value': 60,
            'value change': 10,
            'tower type': 'Speed',
        },
   }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'retraction_enable': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, True),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
    }

    _towerTypesModel = [
        {'value': 'Distance', 'label': 'DST'}, 
        {'value': 'Speed', 'label': 'SPD'}, 
    ]



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__("Retraction Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable, pluginName)



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



    # The starting retraction value for the tower
    _startValueStr = '1'

    startValueStrChanged = pyqtSignal()

    def setStartValueStr(self, value)->None:
        self._startValueStr = value
        self.startValueStrChanged.emit()

    @pyqtProperty(str, notify=startValueStrChanged, fset=setStartValueStr)
    def startValueStr(self)->str:
        return self._startValueStr



    # The ending retraction value for the tower
    _endValueStr = '6'
    
    endValueStrChanged = pyqtSignal()

    def setEndValueStr(self, value)->None:
        self._endValueStr = value
        self.endValueStrChanged.emit()

    @pyqtProperty(str, notify=endValueStrChanged, fset=setEndValueStr)
    def endValueStr(self)->str:
        return self._endValueStr



    # The amount to change the retraction value between tower sections
    _valueChangeStr = '1'

    valueChangeStrChanged = pyqtSignal()

    def setValueChange(self, value)->None:
        self._valueChangeStr = value
        self.valueChangeStrChanged.emit()

    @pyqtProperty(str, notify=valueChangeStrChanged, fset=setValueChange)
    def valueChangeStr(self)->str:
        return self._valueChangeStr



    # The label to carve at the bottom of the tower
    _towerLabelStr = _towerTypesModel[0]['label']

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = 'RETRAC'

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
            Logger.log('e', f'A Retract Tower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset values
        try:
            self._startValue = presetTable['starting value']
            self._valueChange = presetTable['value change']
            self._towerType = presetTable['tower type']
        except KeyError as e:
            Logger.log('e', f'The "{e.args[0]}" entry does not exit for the Retract Tower preset "{presetName}"')
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
        startValue = float(self.startValueStr)
        endValue = float(self.endValueStr)
        valueChange = float(self.valueChangeStr)
        towerLabel = self.towerLabelStr
        towerDescription = self.towerDescriptionStr

        # Ensure the change amount has the correct sign
        valueChange = self._correctChangeValueSign(valueChange, startValue, endValue)

        # Calculate the optimal base and section height, given the current printing layer height
        baseHeight = self._calculateOptimalHeight(self._nominalBaseHeight)
        sectionHeight = self._calculateOptimalHeight(self._nominalSectionHeight)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startValue
        openScadParameters ['Ending_Value'] = endValue
        openScadParameters ['Value_Change'] = valueChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        openScadParameters ['Column_Label'] = towerLabel

        # Record the tower settings that will be needed for post-processing
        self._startValue = startValue
        self._valueChange = valueChange
        self._baseHeight = baseHeight
        self._sectionHeight = sectionHeight

        # Determine the tower name
        towerName = f'Custom Retraction Tower - {self._towerType} {startValue}-{endValue}x{valueChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(
            gcode, 
            self._baseHeight, 
            self._sectionHeight, 
            self._initialLayerHeight, 
            self._layerHeight, 
            self._relativeExtrusion,
            self._startValue, 
            self._valueChange, 
            self._towerType, 
            enable_lcd_messages
            )

        return gcode
