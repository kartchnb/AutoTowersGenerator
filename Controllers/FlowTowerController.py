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

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0

    _presetsTable = {
        '115-85': {
            'filename': 'flowtower 115-85.stl',
            'start value': 115,
            'change value': -5,
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': False,
        'layer_height': None,
        'meshfix_union_all_remove_holes': False,
        'support_enable': False,
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__("Flow Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable)



    # The starting value for the tower
    _startValueStr = '85'

    startValueStrChanged = pyqtSignal()
    
    def setStartValueStr(self, value)->None:
        self._startValueStr = value
        self.startValueStrChanged.emit()

    @pyqtProperty(str, notify=startValueStrChanged, fset=setStartValueStr)
    def startValueStr(self)->str:
        return self._startValueStr



    # The ending value for the tower
    _endValueStr = '115'

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



    # The square size of each tower section (in mm)
    _sectionSizeStr = '10'

    sectionSizeStrChanged = pyqtSignal()
    
    def setSectionSizeStr(self, value)->None:
        self._sectionSizeStr = value
        self.sectionSizeStrChanged.emit()

    @pyqtProperty(str, notify=sectionSizeStrChanged, fset=setSectionSizeStr)
    def sectionSizeStr(self)->str:
        return self._sectionSizeStr



    # The diameter of the hole in each section (in mm)
    _sectionHoleDiameterStr = '5'

    sectionHoleDiameterStrChanged = pyqtSignal()
    
    def setSectionHoleDiameterStr(self, value)->None:
        self._sectionHoleDiameterStr = value
        self.sectionHoleDiameterStrChanged.emit()

    @pyqtProperty(str, notify=sectionHoleDiameterStrChanged, fset=setSectionHoleDiameterStr)
    def sectionHoleDiameterStr(self)->str:
        return self._sectionHoleDiameterStr



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

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Flow Tower {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Read the parameters directly from the dialog
        startValue = float(self.startValueStr)
        endValue = float(self.endValueStr)
        valueChange = float(self.valueChangeStr)
        sectionSize = float(self.sectionSizeStr)
        sectionHoleDiameter = float(self.sectionHoleDiameterStr)
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
        openScadParameters ['Section_Size'] = sectionSize
        openScadParameters ['Section_Hole_Diameter'] = sectionHoleDiameter
        openScadParameters ['Tower_Label'] = towerLabel
        openScadParameters ['Temperature_Label'] = temperatureLabel

        # Determine the tower name
        towerName = f'Auto-Generated Flow Tower {startValue}-{endValue}x{valueChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        gcode = FlowTower_PostProcessing.execute(gcode, self._startValue, self._valueChange, self._sectionLayers, self._baseLayers)

        return gcode
