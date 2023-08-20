# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

from UM.Logger import Logger

from .ControllerBase import ControllerBase
from ..Models.RetractTowerModel import RetractTowerModel

# Import the scripts that do the actual post-processing
from ..Postprocessing import RetractSpeedTower_PostProcessing
from ..Postprocessing import RetractDistanceTower_PostProcessing



class RetractTowerController(ControllerBase):

    _openScadFilename = 'retracttower.scad'
    _qmlFilename = 'RetractTowerDialog.qml'

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'retraction_enable': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, True),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateStlCallback, pluginName):
        dataModel = RetractTowerModel(stlPath=stlPath)
        super().__init__(name="Retraction Tower", guiPath=guiPath, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetName != 'Custom':
            # Load a preset tower
            self._loadPresetRetractTower()
        else:
            # Generate a custom tower using the user's settings
            self.generateCustomRetractTower()



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, input_gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Gather the post-processing values
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        initialLayerHeight = self._dataModel.initialLayerHeight
        layerHeight = self._dataModel.layerHeight
        startValue = self._dataModel.startValue
        valueChange = self._dataModel.valueChange

        # Call the retract speed post-processing script
        if self._towerType == 'Speed':
            output_gcode = RetractSpeedTower_PostProcessing.execute(
                gcode=input_gcode, 
                base_height=baseHeight,
                section_height=sectionHeight, 
                initial_layer_height=initialLayerHeight, 
                layer_height=layerHeight, 
                start_retract_speed=startValue, 
                retract_speed_change=valueChange, 
                enable_lcd_messages=enable_lcd_messages
                )

        # Call the retract distance post-processing script
        else:
            # Call the post-processing script
            output_gcode = RetractDistanceTower_PostProcessing.execute(
                gcode=input_gcode, 
                base_height=baseHeight,
                section_height=sectionHeight, 
                initial_layer_height=initialLayerHeight, 
                layer_height=layerHeight, 
                start_retract_distance=startValue, 
                retract_distance_change=valueChange, 
                enable_lcd_messages=enable_lcd_messages
                )

        return output_gcode



    def _loadPresetRetractTower(self)->None:
        ''' Load a preset tower '''

        # Determine the path of the STL file to load
        stlFilePath = self._dataModel.presetFilePath

        # Determine the tower name
        towerName = f'Preset {self._dataModel.presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(self, towerName, stlFilePath, self.postProcess)



    def generateCustomRetractTower(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        
        # Collect the tower customizations
        openScadFilename = self._openScadFilename
        startValue = self._dataModel.startValue
        endValue = self._dataModel.endValue
        valueChange = self._dataModel.valueChange
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        towerLabel = self._dataModel.towerLabel
        towerDescription = self._dataModel.towerDescription

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
        towerName = f'Custom Retraction Tower - {self._dataModel.towerTypeName} {startValue}-{endValue}x{valueChange}'

        # Send the filename and parameters to the model callback
        self._generateStlCallback(self, towerName, openScadFilename, openScadParameters, self.postProcess)
