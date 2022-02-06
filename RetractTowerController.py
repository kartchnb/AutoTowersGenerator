import os
import math

from PyQt5.QtCore import QObject, pyqtSlot

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger

# Import the script that does the actual post-processing
from .scripts import RetractTower_PostProcessing



class RetractTowerController(QObject):
    _openScadFilename = 'retracttower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, pluginPath, modelCallback):
        QObject.__init__(self)

        self._pluginPath = pluginPath
        
        self._dialog = None
        self._towerType = ''

        self._modelCallback = modelCallback

        self._baseLayers = 0
        self._sectionLayers = 0



    # Create a dialog from a .qml file
    def _createDialog(self, qml_filename):
        qml_file_path = os.path.join(self._pluginPath, 'gui', qml_filename)
        dialog = Application.getInstance().createQmlComponent(qml_file_path, {'manager': self})
        return dialog


    
    _cachedSpeedTowerDialog = None
    @property
    def _speedTowerDialog(self):
        if self._cachedSpeedTowerDialog == None:
            self._cachedSpeedTowerDialog = self._createDialog('RetractSpeedTowerDialog.qml')
        return self._cachedSpeedTowerDialog


    
    _cachedDistanceTowerDialog = None
    @property
    def _distanceTowerDialog(self):
        if self._cachedDistanceTowerDialog == None:
            self._cachedDistanceTowerDialog = self._createDialog('RetractDistanceTowerDialog.qml')
        return self._cachedDistanceTowerDialog



    def generate(self, towerType):
        self._towerType = towerType

        # Show the appropriate dialog
        if towerType == 'distance':
            self._dialog = self._distanceTowerDialog
        elif towerType == 'speed':
            self._dialog = self._speedTowerDialog

        self._dialog.show()



    # This function is called when the 'Generate' button on the temp tower settings dialog is clicked
    @pyqtSlot()
    def dialogAccepted(self):
        # Read the parameters directly from the dialog
        startValue = int(self._dialog.property('startValue'))
        endValue = int(self._dialog.property('endValue'))
        valueChange = int(self._dialog.property('valueChange'))
        towerDescription = self._dialog.property('towerDescription')

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

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startValue
        openScadParameters ['Ending_Value'] = endValue
        openScadParameters ['Value_Change'] = valueChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        if self._towerType == 'distance':
            openScadParameters ['Column_Label'] = 'DIST'
        elif self._towerType == 'speed':
            openScadParameters ['Column_Label'] = 'SPD'

        # Send the filename and parameters to the model callback
        self._modelCallback(self._openScadFilename, openScadParameters, self.postProcess)



    # This code was modified from the RetractTower.py post-processing script
    # provided as part of 5axes' CalibrationShapes plugin
    def postProcess(self, gcode):
        # Read the parameters from the dialog
        startValue = int(self._dialog.property('startValue'))
        valueChange = int(self._dialog.property('valueChange'))

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(gcode, startValue, valueChange, self._sectionLayers, self._baseLayers, self._towerType)

        return gcode
