# Import the correct version of PyQt
try:
    from PyQt6.QtCore import pyqtSlot
except ImportError:
    from PyQt5.QtCore import pyqtSlot

import os

from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Resources import Resources

from .ControllerBase import ControllerBase
from ..Models.FanTowerModel import FanTowerModel

# Import the script that does the actual post-processing
from ..Postprocessing import FanTower_PostProcessing

Resources.addSearchPath(
    os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'),'Resources')
)  # Plugin translation file import
catalog = i18nCatalog("autotowers")


class FanTowerController(ControllerBase):

    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'FanTowerDialog.qml'



    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiDir, stlDir, loadStlCallback, generateStlCallback, pluginName):
        dataModel = FanTowerModel(stlDir=stlDir)
        super().__init__(name=catalog.i18nc("@test", "Fan Tower"), guiDir=guiDir, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetSelected:
            # Load a preset tower
            self._loadPresetFanTower()
        else:
            # Generate a custom tower using the user's settings
            self._generateCustomFanTower()



    def postProcess(self, gcode, enable_lcd_messages=False, enable_advanced_gcode_comments=True)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Determine the post-processing values
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        initialLayerHeight = self._dataModel.initialLayerHeight
        layerHeight = self._dataModel.layerHeight
        startFanPercent = self._dataModel.startFanPercent
        fanPercentChange = self._dataModel.fanPercentChange
        maintainBridgeValue = self._dataModel.maintainBridgeValue

        # Call the post-processing script
        gcode = FanTower_PostProcessing.execute(
            gcode=gcode, 
            base_height=baseHeight, 
            section_height=sectionHeight, 
            initial_layer_height=initialLayerHeight,
            layer_height=layerHeight, 
            start_fan_percent=startFanPercent,
            fan_percent_change=fanPercentChange, 
            maintain_bridge_value=maintainBridgeValue,
            enable_lcd_messages=enable_lcd_messages,
            enable_advanced_gcode_comments=enable_advanced_gcode_comments
            )

        return gcode



    def _loadPresetFanTower(self)->None:
        ''' Load a preset tower '''

        # Determine the path of the STL file to load
        stlFilePath = self._dataModel.presetFilePath

        # Determine the tower name
        towerName = f'Preset {self._dataModel.presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    def _generateCustomFanTower(self)->None:
        ''' Generate a custom tower '''

        # Collect data from the data model
        openScadFilename = self._openScadFilename
        startFanPercent = self._dataModel.startFanPercent
        endFanPercent = self._dataModel.endFanPercent
        fanPercentChange = self._dataModel.fanPercentChange
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        towerLabel = self._dataModel.towerLabel
        towerDescription = self._dataModel.towerDescription

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {
            'Starting_Value': startFanPercent,
            'Ending_Value': endFanPercent,
            'Value_Change': fanPercentChange,
            'Base_Height': baseHeight,
            'Section_Height': sectionHeight,
            'Column_Label': towerLabel,
            'Tower_Label': towerDescription,
        }

        # Determine the tower name
        towerName = f'Custom Fan Tower - Speed {startFanPercent}-{endFanPercent}x{fanPercentChange}'

        # Send the filename and parameters to the STL generation callback
        self._generateStlCallback(self, towerName, openScadFilename, openScadParameters, self.postProcess)
