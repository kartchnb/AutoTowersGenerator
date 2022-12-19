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
    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'FlowTowerDialog.qml'

    _presetsTable = {
        'Flow Tower - Flow 115-85': {
            'starting flow': 115,
            'flow change': -5,
        },
    }

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, pluginName):
        super().__init__("Flow Tower", guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, self._openScadFilename, self._qmlFilename, self._presetsTable, self._criticalPropertiesTable, pluginName)



    # The starting flow percent for the tower
    _startFlowStr = '115'

    startFlowStrChanged = pyqtSignal()
    
    def setStartFlowStr(self, value)->None:
        self._startFlowStr = value
        self.startFlowStrChanged.emit()

    @pyqtProperty(str, notify=startFlowStrChanged, fset=setStartFlowStr)
    def startFlowStr(self)->str:
        return self._startFlowStr



    # The ending flow percent for the tower
    _endFlowStr = '85'

    endFlowStrChanged = pyqtSignal()
    
    def setEndFlowStr(self, value)->None:
        self._endFlowStr = value
        self.endFlowStrChanged.emit()

    @pyqtProperty(str, notify=endFlowStrChanged, fset=setEndFlowStr)
    def endFlowStr(self)->str:
        return self._endFlowStr



    # The amount to change the flow between tower sections
    _flowChangeStr = '5'

    flowChangeStrChanged = pyqtSignal()
    
    def setFlowChangeStr(self, value)->None:
        self._flowChangeStr = value
        self.flowChangeStrChanged.emit()

    @pyqtProperty(str, notify=flowChangeStrChanged, fset=setFlowChangeStr)
    def flowChangeStr(self)->str:
        return self._flowChangeStr



    # The label to add to the tower
    _towerLabelStr = 'FLW'

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The description to add to the side of the tower
    _towerDescriptionStr = 'FLOW'

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
            Logger.log('e', f'A Flow Tower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset values
        try:
            self._startFlow = presetTable['starting flow']
            self._valueChange = presetTable['flow change']
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
        # Read the parameters directly from the dialog
        startFlow = float(self.startFlowStr)
        endFlow = float(self.endFlowStr)
        flowChange = float(self.flowChangeStr)
        towerLabel = self.towerLabelStr
        towerDescription = self.towerDescriptionStr

        # Ensure the change amount has the correct sign
        flowChange = self._correctChangeValueSign(flowChange, startFlow, endFlow)

        # Calculate the optimal base and section height, given the current printing layer height
        baseHeight = self._calculateOptimalHeight(self._nominalBaseHeight)
        sectionHeight = self._calculateOptimalHeight(self._nominalSectionHeight)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startFlow
        openScadParameters ['Ending_Value'] = endFlow
        openScadParameters ['Value_Change'] = flowChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Record the tower settings that will be needed for post-processing
        self._startFlow = startFlow
        self._flowChange = flowChange
        self._baseHeight = baseHeight
        self._sectionHeight = sectionHeight

        # Determine the tower name
        towerName = f'Custom Flow Tower - {startFlow}-{endFlow}x{flowChange}'

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
            self._startFlow, 
            self._flowChange, 
            enable_lcd_messages
            )

        return gcode
