# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

from UM.Logger import Logger

from .ControllerBase import ControllerBase
from ..Models.TempTowerModel import TempTowerModel

# Import the script that does the actual post-processing
from ..Postprocessing import TempTower_PostProcessing



class TempTowerController(ControllerBase):

    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'TempTowerDialog.qml'

    _criticalPropertiesTable = {
        'adaptive_layer_height_enabled': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
        'layer_height': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, None),
        'meshfix_union_all_remove_holes': (ControllerBase.ContainerId.ACTIVE_EXTRUDER_STACK, False),
        'support_enable': (ControllerBase.ContainerId.GLOBAL_CONTAINER_STACK, False),
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateStlCallback, pluginName):
        dataModel = TempTowerModel(stlPath=stlPath)
        super().__init__(name='Temp Tower', guiPath=guiPath, loadStlCallback=loadStlCallback, generateStlCallback=generateStlCallback, qmlFilename=self._qmlFilename, criticalPropertiesTable=self._criticalPropertiesTable, dataModel=dataModel, pluginName=pluginName)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        if self._dataModel.presetName != 'Custom':
            # Load a preset tower
            self._loadPresetTempTower()
        else:
            # Generate a custom tower using the user's settings
            self._generateCustomTempTower()



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode, enable_lcd_messages=False)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Collect the post-processing data
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        initialLayerHeight = self._dataModel.initialLayerHeight
        layerHeight = self._dataModel.layerHeight
        startTemperature = self._dataModel.startTemperature
        temperatureChange = self._dataModel.temperatureChange

        # Call the post-processing script
        gcode = TempTower_PostProcessing.execute(
            gcode=gcode, 
            base_height=baseHeight,
            section_height=sectionHeight,
            initial_layer_height=initialLayerHeight,
            layer_height=layerHeight,
            start_temp=startTemperature,
            temp_change=temperatureChange,
            enable_lcd_messages=enable_lcd_messages
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
        startTemperature = self._dataModel.startTemperature
        endTemperature = self._dataModel.endTemperature
        temperatureChange = self._dataModel.temperatureChange
        baseHeight = self._dataModel.optimalBaseHeight
        sectionHeight = self._dataModel.optimalSectionHeight
        towerLabel = self._dataModel.towerLabel
        towerDescription = self._dataModel.towerDescription

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startTemperature
        openScadParameters ['Ending_Value'] = endTemperature
        openScadParameters ['Value_Change'] = temperatureChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Determine the tower name
        towerName = f'Custom Temp Tower - {startTemperature}-{endTemperature}x{temperatureChange}'

        # Send the filename and parameters to the model callback
        self._generateStlCallback(self, towerName, self._openScadFilename, openScadParameters, self.postProcess)
