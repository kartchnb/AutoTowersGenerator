# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

import os

from UM.Logger import Logger
from UM.i18n import i18nCatalog
from UM.Resources import Resources

from .ControllerBase import ControllerBase
from ..Models.TempTowerModel import TempTowerModel

# Import the script that does the actual post-processing
from ..Postprocessing import TempTower_PostProcessing

Resources.addSearchPath(
    os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'),'Resources')
)  # Plugin translation file import
catalog = i18nCatalog("autotowers")

class TempTowerController(ControllerBase):

    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'TempTowerDialog.qml'

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiDir, stlDir, loadStlCallback, generateStlCallback, pluginName):
        dataModel = TempTowerModel(stlDir=stlDir)
        super().__init__(name=catalog.i18nc("@test", "Temp Tower"), guiDir=guiDir, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetSelected:
            # Load a preset tower
            self._loadPresetTempTower()
        else:
            # Generate a custom tower using the user's settings
            self._generateCustomTempTower()



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enable_lcd_messages=False, enable_advanced_gcode_comments=True)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Collect the post-processing data
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        initialLayerHeight = self._dataModel.initialLayerHeight
        layerHeight = self._dataModel.layerHeight
        startTemp = self._dataModel.startTemp
        tempChange = self._dataModel.tempChange

        # Call the post-processing script
        gcode = TempTower_PostProcessing.execute(
            gcode=gcode, 
            base_height=baseHeight,
            section_height=sectionHeight,
            initial_layer_height=initialLayerHeight,
            layer_height=layerHeight,
            start_temp=startTemp,
            temp_change=tempChange,
            enable_lcd_messages=enable_lcd_messages,
            enable_advanced_gcode_comments = enable_advanced_gcode_comments
            )

        return gcode



    def _loadPresetTempTower(self)->None:
        ''' Load a preset tower '''

        # Determine the path of the STL file to load
        stlFilePath = self._dataModel.presetFilePath

        # Determine the tower name
        towerName = f'Preset {self._dataModel.presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    def _generateCustomTempTower(self)->None:
        ''' Generate a custom tower '''

        # Collect data from the data model
        openScadFilename = self._openScadFilename
        startTemp = self._dataModel.startTemp
        endTemp = self._dataModel.endTemp
        tempChange = self._dataModel.tempChange
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        towerLabel = self._dataModel.towerLabel
        towerDescription = self._dataModel.towerDescription

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startTemp
        openScadParameters ['Ending_Value'] = endTemp
        openScadParameters ['Value_Change'] = tempChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Determine the tower name
        towerName = f'Custom Temp Tower - {startTemp}-{endTemp}x{tempChange}'

        # Send the filename and parameters to the model callback
        self._generateStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)
