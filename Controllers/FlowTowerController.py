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
from ..Postprocessing import FlowTower_PostProcessing



class FlowTowerController(ControllerBase):
    _openScadFilename = 'flowtower.scad'
    _qmlFilename = 'FlowTowerDialog.qml'

    _presetsTable = {
        '115-85': {
            'filename': 'flowtower 115-85.stl',
            'starting value': 115,
            'value change': -5,
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'infill_sparse_density': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, 0),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__("Flow Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable)



    # The starting value for the tower
    _startValueStr = '115'

    startValueStrChanged = pyqtSignal()
    
    def setStartValueStr(self, value)->None:
        self._startValueStr = value
        self.startValueStrChanged.emit()

    @pyqtProperty(str, notify=startValueStrChanged, fset=setStartValueStr)
    def startValueStr(self)->str:
        return self._startValueStr



    # The ending value for the tower
    _endValueStr = '85'

    endValueStrChanged = pyqtSignal()
    
    def setEndValueStr(self, value)->None:
        self._endValueStr = value
        self.endValueStrChanged.emit()

    @pyqtProperty(str, notify=endValueStrChanged, fset=setEndValueStr)
    def endValueStr(self)->str:
        return self._endValueStr



    # The amount to change the value between tower sections
    _valueChangeStr = '5'

    valueChangeStrChanged = pyqtSignal()
    
    def setValueChangeStr(self, value)->None:
        self._valueChangeStr = value
        self.valueChangeStrChanged.emit()

    @pyqtProperty(str, notify=valueChangeStrChanged, fset=setValueChangeStr)
    def valueChangeStr(self)->str:
        return self._valueChangeStr



    # The label to add to the tower
    _towerLabelStr = 'FLOW'

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
            Logger.log('e', f'A FlowTower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset values
        try:
            stlFileName = presetTable['filename']
            self._startValue = presetTable['starting value']
            self._valueChange = presetTable['value change']
        except KeyError as e:
            Logger.log('e', f'The "{e.args[0]}" entry does not exit for the FanTower preset "{presetName}"')
            return

        # Use the nominal base and section heights for this preset tower
        self._baseHeight = self._nominalBaseHeight
        self._sectionHeight = self._nominalSectionHeight

        # Determine the file path of the preset
        stlFilePath = self._getStlFilePath(stlFileName)

        # Determine the tower name
        towerName = f'Preset Flow Tower {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Read the parameters directly from the dialog
        startValue = float(self.startValueStr)
        endValue = float(self.endValueStr)
        valueChange = float(self.valueChangeStr)
        towerLabel = self.towerLabelStr
        temperatureLabel = self.temperatureLabelStr

        # Ensure the value change has the correct sign
        valueChange = self._correctChangeValueSign(valueChange, startValue, endValue)

        # Calculate the optimal base and section height, given the current printing layer height
        baseHeight = self._calculateOptimalHeight(self._nominalBaseHeight)
        sectionSize = self._calculateOptimalHeight(self._nominalSectionHeight)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startValue
        openScadParameters ['Ending_Value'] = endValue
        openScadParameters ['Value_Change'] = valueChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Size'] = sectionSize
        openScadParameters ['Tower_Label'] = towerLabel
        openScadParameters ['Temperature_Label'] = temperatureLabel

        # Record the tower settings that will be needed for post-processing
        self._startValue = startValue
        self._valueChange = valueChange
        self._baseHeight = baseHeight
        self._sectionHeight = sectionSize

        # Determine the tower name
        towerName = f'Custom Flow Tower {startValue}-{endValue}x{valueChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        gcode = FlowTower_PostProcessing.execute(
            gcode, 
            self._baseHeight, 
            self._sectionHeight, 
            self._initialLayerHeight, 
            self._layerHeight, 
            self._startValue, 
            self._valueChange, 
            enable_lcd_messages
            )

        return gcode
