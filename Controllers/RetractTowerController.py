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
        'Distance 1-6': {
            'filename': 'retracttower distance 1-6.stl',
            'start value': 1,
            'change value': 1,
            'tower type': 'Distance',
        },

        'Distance 4-9': {
            'filename': 'retracttower distance 4-9.stl',
            'start value': 4,
            'change value': 1,
            'tower type': 'Distance',
        },

        'Distance 7-12': {
            'filename': 'retracttower distance 7-12.stl',
            'start value': 7,
            'change value': 1,
            'tower type': 'Distance',
        },
 
         'Speed 10-50': {
            'filename': 'retracttower speed 10-50.stl',
            'start value': 10,
            'change value': 10,
            'tower type': 'Speed',
        },

        'Speed 35-75': {
            'filename': 'retracttower speed 35-75.stl',
            'start value': 35,
            'change value': 10,
            'tower type': 'Speed',
        },

        'Speed 60-100': {
            'filename': 'retracttower speed 60-100.stl',
            'start value': 60,
            'change value': 10,
            'tower type': 'Speed',
        },
   }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': ('global', False),
        'layer_height': ('global', None),
        'meshfix_union_all_remove_holes': ('extruder', False),
    }

    _towerTypesModel = [
        {'value': 'Distance', 'label': 'DST'}, 
        {'value': 'Speed', 'label': 'SPD'}, 
    ]

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__("Retraction Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable)



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
    _towerDescriptionStr = 'RETRACTION'

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value)->None:
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self)->str:
        return self._towerDescriptionStr



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetsTable[presetName]
        except KeyError:
            Logger.log('e', f'A RetractTower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for RetractTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's starting value
        try:
            self._startValue = presetTable['start value']
        except KeyError:
            Logger.log('e', f'The "start value" for RetractTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's value change value
        try:
            self._valueChange = presetTable['change value']
        except KeyError:
            Logger.log('e', f'The "change value" for RetractTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's tower type value
        try:
            self._towerType = presetTable['tower type']
        except KeyError:
            Logger.log('e', f'The "tower type" for RetractTower preset table "{presetName}" has not been defined')
            return

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Retraction Value Tower {presetName}'

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

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty('layer_height', 'value')

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        baseHeight = self._baseLayers * layerHeight

        # Correct the section height to ensure an integer number of layers per section
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up
        sectionHeight = self._sectionLayers * layerHeight

        # Ensure the change amount has the correct sign
        if endValue >= startValue:
            valueChange = abs(valueChange)
        else:
            valueChange = -abs(valueChange)

        # Record the tower settings that will be needed for post-processing
        self._startValue = startValue
        self._valueChange = valueChange

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startValue
        openScadParameters ['Ending_Value'] = endValue
        openScadParameters ['Value_Change'] = valueChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        openScadParameters ['Column_Label'] = towerLabel

        # Determine the tower name
        towerName = f'Auto-Generated Retraction Tower ({self._towerType}) {startValue}-{endValue}x{valueChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, displayOnLcd=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(gcode, self._startValue, self._valueChange, self._sectionLayers, self._baseLayers, self._towerType, displayOnLcd)

        return gcode
