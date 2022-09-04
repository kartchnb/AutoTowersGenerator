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

# Import the script that does the actual post-processing
from .scripts import RetractTower_PostProcessing



class RetractSpeedTowerController(QObject):
    _openScadFilename = 'retracttower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, guiPath, modelCallback):
        QObject.__init__(self)
        
        self._modelCallback = modelCallback

        # Prepare the settings dialogs
        qml_file_path = os.path.join(guiPath, 'RetractSpeedTowerDialog.qml')
        self._dialog = CuraApplication.getInstance().createQmlComponent(qml_file_path, {'manager': self})

        self._baseLayers = 0
        self._sectionLayers = 0



    # The starting retraction speed
    _startSpeedStr = '10'

    startSpeedStrChanged = pyqtSignal()

    def setStartSpeedStr(self, value):
        self._startSpeedStr = value
        self.startSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startSpeedStrChanged, fset=setStartSpeedStr)
    def startSpeedStr(self) -> str:
        return self._startSpeedStr



    # The ending retraction speed
    _endSpeedStr = '40'

    endSpeedStrChanged = pyqtSignal()

    def setEndSpeedStr(self, value):
        self._endSpeedStr = value
        self.endSpeedStrChanged.emit()

    @pyqtProperty(str, notify=endSpeedStrChanged, fset=setEndSpeedStr)
    def endSpeedStr(self) -> str:
        return self._endSpeedStr



    # The amount to change the retraction speed between tower sections
    _speedChangeStr = '10'

    speedChangeStrChanged = pyqtSignal()

    def setSpeedChange(self, value):
        self._speedChangeStr = value
        self.speedChangeStrChanged.emit()

    @pyqtProperty(str, notify=speedChangeStrChanged, fset=setSpeedChange)
    def speedChangeStr(self) -> str:
        return self._speedChangeStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = ''

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value):
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self) -> str:
        return self._towerDescriptionStr



    def generate(self):
        self._dialog.show()



    # This function is called when the 'Generate' button on the temp tower settings dialog is clicked
    @pyqtSlot()
    def dialogAccepted(self):
        # Determine the parameters for the tower
        startSpeed = float(self.startSpeedStr)
        endSpeed = float(self.endSpeedStr)
        speedChange = float(self.speedChangeStr)
        towerDescription = self.towerDescriptionStr

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty('layer_height', 'value')

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        baseHeight = self._baseLayers * layerHeight

        # Correct the section height to ensure an integer number of layers per section
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up
        sectionHeight = self._sectionLayers * layerHeight

        # Ensure the change amount has the correct sign
        if endSpeed >= startSpeed:
            speedChange = abs(speedChange)
        else:
            speedChange = -abs(speedChange)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startSpeed
        openScadParameters ['Ending_Value'] = endSpeed
        openScadParameters ['Value_Change'] = speedChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        openScadParameters ['Column_Label'] = 'SPD'

        # Send the filename and parameters to the model callback
        self._modelCallback(self._openScadFilename, openScadParameters, self.postProcess)



    # This code was modified from the RetractTower.py post-processing script
    # provided as part of 5axes' CalibrationShapes plugin
    def postProcess(self, gcode):
        # Determine the parameters for the tower
        startSpeed = float(self.startSpeedStr)
        speedChange = float(self.speedChangeStr)

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(gcode, startSpeed, speedChange, self._sectionLayers, self._baseLayers, 'speed')

        return gcode
