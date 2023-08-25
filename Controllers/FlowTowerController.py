import os
import math

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSlot
except ImportError:
    from PyQt5.QtCore import pyqtSlot

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Resources import Resources

from .ControllerBase import ControllerBase
from ..Models.FlowTowerModel import FlowTowerModel

# Import the script that does the actual post-processing
from ..Postprocessing import FlowTower_PostProcessing

Resources.addSearchPath(
    os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'),'Resources')
)  # Plugin translation file import
catalog = i18nCatalog("autotowers")


class FlowTowerController(ControllerBase):

    _qmlFilename = 'FlowTowerDialog.qml'



    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiDir, stlDir, loadStlCallback, generateStlCallback, pluginName):
        dataModel = FlowTowerModel(stlDir=stlDir)
        super().__init__(name=catalog.i18nc("@test", "Flow Tower"), guiDir=guiDir, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetSelected:
            # Load a preset tower
            self._loadPresetFlowTower()
        else:
            # Generate a custom tower using the user's settings
            self._generateCustomFlowTower()



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, input_gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Determine the post-processing values
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        initialLayerHeight = self._dataModel.initialLayerHeight
        layerHeight = self._dataModel.layerHeight
        relativeExtrusion = self._dataModel.relativeExtrusion
        startFlowPercent = self._dataModel.startFlowPercent
        flowPercentChange = self._dataModel.flowPercentChange
        currentFlowRate = self._dataModel.flowRate

        # Call the post-processing script
        output_gcode = FlowTower_PostProcessing.execute(
            gcode=input_gcode, 
            base_height=baseHeight,
            section_height=sectionHeight, 
            initial_layer_height=initialLayerHeight, 
            layer_height=layerHeight, 
            relative_extrusion=relativeExtrusion,
            start_flow_rate=startFlowPercent, 
            flow_rate_change=flowPercentChange, 
            reference_flow_rate=currentFlowRate,
            enable_lcd_messages=enable_lcd_messages
            )

        return output_gcode



    def _loadPresetFlowTower(self)->None:
        ''' Load a preset tower '''

        # Determine the path of the STL file to load
        stlFilePath = self._dataModel.presetFilePath

        # Determine the tower name
        towerName = f'Preset {self._dataModel.presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    def _generateCustomFlowTower(self)->None:
        ''' Generate a custom tower '''

        # Collect data from the data model
        openScadFileName = self._dataModel.towerDesignFileName
        startFlowPercent = self._dataModel.startFlowPercent
        endFlowPercent = self._dataModel.endFlowPercent
        flowPercentChange = self._dataModel.flowPercentChange
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        towerLabel = self._dataModel.towerLabel
        towerDescription = self._dataModel.towerDescription

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startFlowPercent
        openScadParameters ['Ending_Value'] = endFlowPercent
        openScadParameters ['Value_Change'] = flowPercentChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Temperature_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Determine the tower name
        towerName = f'Custom Flow Tower - {startFlowPercent}-{endFlowPercent}x{flowPercentChange}'

        # Send the filename and parameters to the model callback
        self._generateStlCallback(self, towerName, openScadFileName, openScadParameters, self.postProcess)
