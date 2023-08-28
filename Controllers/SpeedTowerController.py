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
from ..Models.SpeedTowerModel import SpeedTowerModel

# Import the scripts that do the actual post-processing
from ..Postprocessing import PrintSpeedTower_PostProcessing
from ..Postprocessing import MiscSpeedTower_PostProcessing

Resources.addSearchPath(
    os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'),'Resources')
)  # Plugin translation file import
catalog = i18nCatalog("autotowers")

class SpeedTowerController(ControllerBase):

    _openScadFilename = 'speedtower.scad'
    _qmlFilename = 'SpeedTowerDialog.qml'

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiDir, stlDir, loadStlCallback, generateStlCallback, pluginName):
        dataModel = SpeedTowerModel(stlDir=stlDir)
        super().__init__(name=catalog.i18nc("@test", "Speed Tower"), guiDir=guiDir, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetSelected:
            # Load a preset tower
            self._loadPresetSpeedTower()
        else:
            # Generate a custom tower using the user's settings
            self._generateCustomSpeedTower()



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enableLcdMessages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Determine the post-processing values
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        initialLayerHeight = self._dataModel.initialLayerHeight
        layerHeight = self._dataModel.layerHeight
        startSpeed = self._dataModel.startSpeed
        speedChange = self._dataModel.speedChange
        towerType = self._dataModel.towerTypeName

        # Call the post-processing script for print speed towers
        if towerType == 'Print Speed':
            currentPrintSpeed = self._dataModel.printSpeed

            gcode = PrintSpeedTower_PostProcessing.execute(
                gcode=gcode, 
                base_height=baseHeight,
                section_height=sectionHeight,
                initial_layer_height=initialLayerHeight,
                layer_height=layerHeight,
                start_speed=startSpeed,
                speed_change=speedChange,
                reference_speed=currentPrintSpeed,
                enable_lcd_messages=enableLcdMessages,
                enable_advanced_gcode_comments=enableAdvancedGcodeComments
                )
        
        # Call the post-processing script for non print speed towers
        else:
            gcode = MiscSpeedTower_PostProcessing.execute(
                gcode=gcode, 
                base_height=baseHeight,
                section_height=sectionHeight,
                initial_layer_height=initialLayerHeight,
                layer_height=layerHeight,
                start_speed=startSpeed,
                speed_change=speedChange,
                tower_type=towerType,
                enable_lcd_messages=enableLcdMessages,
                enable_advanced_gcode_comments=enableAdvancedGcodeComments
                )

        return gcode



    def _loadPresetSpeedTower(self)->None:
        ''' Load a preset tower '''

        # Determine the path of the STL file to load
        stlFilePath = self._dataModel.presetFilePath

        # Determine the tower name
        towerName = f'Preset {self._dataModel.presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    def _generateCustomSpeedTower(self)->None:
        ''' Generate a custom tower '''

        # Collect data from the data model
        startSpeed = self._dataModel.startSpeed
        endSpeed = self._dataModel.endSpeed
        speedChange = self._dataModel.speedChange
        wingLength = self._dataModel.wingLength
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        towerLabel = self._dataModel.towerLabel
        towerDescription = self._dataModel.towerDescription
        towerType = self._dataModel.towerTypeName
        openScadFilename = self._openScadFilename

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Speed_Value'] = startSpeed
        openScadParameters ['Ending_Speed_Value'] = endSpeed
        openScadParameters ['Speed_Value_Change'] = speedChange
        openScadParameters ['Wing_Length'] = wingLength
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerLabel
        openScadParameters ['Tower_Description'] = towerDescription

        # Determine the tower name
        towerName = f'Custom Speed Tower - {towerType} {startSpeed}-{endSpeed}x{speedChange}'

        # Send the filename and parameters to the model callback
        self._generateStlCallback(self, towerName, openScadFilename, openScadParameters, self.postProcess)
