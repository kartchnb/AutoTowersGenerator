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
from .scripts import FanTower_PostProcessing



class FanTowerController(QObject):
    _openScadFilename = 'temptower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, guiPath, modelCallback):
        QObject.__init__(self)

        self._modelCallback = modelCallback

        # Prepare the settings dialog
        qml_file_path = os.path.join(guiPath, 'FanTowerDialog.qml')
        self._dialog = CuraApplication.getInstance().createQmlComponent(qml_file_path, {'manager': self})

        self._baseLayers = 0
        self._sectionLayers = 0



    # The starting percentage value for the tower
    _startPercentStr = '100'

    startPercentStrChanged = pyqtSignal()
    
    def setStartPercentStr(self, value):
        self._startPercentStr = value
        self.startPercentStrChanged.emit()

    @pyqtProperty(str, notify=startPercentStrChanged, fset=setStartPercentStr)
    def startPercentStr(self) -> str:
        return self._startPercentStr



    # The ending percentage value for the tower
    _endPercentStr = '0'

    endPercentStrChanged = pyqtSignal()
    
    def setEndPercentStr(self, value):
        self._endPercentStr = value
        self.endPercentStrChanged.emit()

    @pyqtProperty(str, notify=endPercentStrChanged, fset=setEndPercentStr)
    def endPercentStr(self) -> str:
        return self._endPercentStr



    # The amount to change the percentage between tower sections
    _percentChangeStr = '-20'

    percentChangeStrChanged = pyqtSignal()
    
    def setPercentChangeStr(self, value):
        self._percentChangeStr = value
        self.percentChangeStrChanged.emit()

    @pyqtProperty(str, notify=percentChangeStrChanged, fset=setPercentChangeStr)
    def percentChangeStr(self) -> str:
        return self._percentChangeStr



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



    @pyqtSlot()
    def dialogAccepted(self):
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        # Read the parameters directly from the dialog
        startPercent = float(self.startPercentStr)
        endPercent = float(self.endPercentStr)
        percentChange = float(self.percentChangeStr)
        towerDescription = self.towerDescriptionStr

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        baseHeight = self._baseLayers * layerHeight

        # Correct the section height to ensure an integer number of layers per section
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up
        sectionHeight = self._sectionLayers * layerHeight

        # Ensure the change amount has the correct sign
        if endPercent >= startPercent:
            percentChange = abs(percentChange)
        else:
            percentChange = -abs(percentChange)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startPercent
        openScadParameters ['Ending_Value'] = endPercent
        openScadParameters ['Value_Change'] = percentChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerDescription
        openScadParameters ['Column_Label'] = 'FAN'

        # Send the filename and parameters to the model callback
        self._modelCallback(self._openScadFilename, openScadParameters, self._postProcess)



    def _postProcess(self, gcode):
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Read the parameters from the dialog
        startPercent = float(self.startPercentStr)
        percentChange = float(self.percentChangeStr)

        # Call the post-processing script
        gcode = FanTower_PostProcessing.execute(gcode, startPercent, percentChange, self._sectionLayers, self._baseLayers)

        return gcode
