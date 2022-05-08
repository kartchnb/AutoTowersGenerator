import os
import math

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger

# Import the script that does the actual post-processing
from .scripts import RetractTower_PostProcessing



class RetractDistanceTowerController(QObject):
    _openScadFilename = 'retracttower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, pluginPath, modelCallback):
        QObject.__init__(self)

        self._pluginPath = pluginPath
        
        self._modelCallback = modelCallback

        # Prepare the settings dialogs
        qml_file_path = os.path.join(pluginPath, 'gui', 'RetractDistanceTowerDialog.qml')
        self._dialog = CuraApplication.getInstance().createQmlComponent(qml_file_path, {'manager': self})

        self._baseLayers = 0
        self._sectionLayers = 0



    # The starting retraction distance
    _startDistanceStr = '1'

    startDistanceStrChanged = pyqtSignal()

    def setStartDistanceStr(self, value):
        self._startDistanceStr = value
        self.startDistanceStrChanged.emit()

    @pyqtProperty(str, notify=startDistanceStrChanged, fset=setStartDistanceStr)
    def startDistanceStr(self) -> str:
        return self._startDistanceStr



    # The ending retraction distance
    _endDistanceStr = '6'
    
    endDistanceStrChanged = pyqtSignal()

    def setEndDistanceStr(self, value):
        self._endDistanceStr = value
        self.endDistanceStrChanged.emit()

    @pyqtProperty(str, notify=endDistanceStrChanged, fset=setEndDistanceStr)
    def endDistanceStr(self) -> str:
        return self._endDistanceStr



    # The amount to change the retraction distance between tower sections
    _distanceChangeStr = '1'

    distanceChangeStrChanged = pyqtSignal()

    def setDistanceChange(self, value):
        self._distanceChangeStr = value
        self.distanceChangeStrChanged.emit()

    @pyqtProperty(str, notify=distanceChangeStrChanged, fset=setDistanceChange)
    def distanceChangeStr(self) -> str:
        return self._distanceChangeStr



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
        startDistance = float(self.startDistanceStr)
        endDistance = float(self.endDistanceStr)
        distanceChange = float(self.distanceChangeStr)
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
        if endDistance >= startDistance:
            distanceChange = abs(distanceChange)
        else:
            distanceChange = -abs(distanceChange)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startDistance
        openScadParameters ['Ending_Value'] = endDistance
        openScadParameters ['Value_Change'] = distanceChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        openScadParameters ['Column_Label'] = 'DIST'

        # Send the filename and parameters to the model callback
        self._modelCallback(self._openScadFilename, openScadParameters, self.postProcess)



    # This code was modified from the RetractTower.py post-processing script
    # provided as part of 5axes' CalibrationShapes plugin
    def postProcess(self, gcode):
        # Determine the parameters for the tower
        startDistance = float(self.startDistanceStr)
        distanceChange = float(self.distanceChangeStr)

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(gcode, startDistance, distanceChange, self._sectionLayers, self._baseLayers, 'speed')

        return gcode
