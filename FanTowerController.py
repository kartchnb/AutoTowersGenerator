import os
import math

from PyQt5.QtCore import QObject, pyqtSlot

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger

# Import the script that does the actual post-processing
from .scripts import FanTower_PostProcessing



class FanTowerController(QObject):
    _openScadFilename = 'temptower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0



    def __init__(self, pluginPath, modelCallback):
        QObject.__init__(self)

        self._modelCallback = modelCallback

        # Prepare the settings dialog
        qml_file_path = os.path.join(pluginPath, 'gui', 'FanTowerDialog.qml')
        self._dialog = CuraApplication.getInstance().createQmlComponent(qml_file_path, {'manager': self})

        self._baseLayers = 0
        self._sectionLayers = 0



    def generate(self):
        self._dialog.show()



    @pyqtSlot()
    def dialogAccepted(self):
        ''' This method is called by the dialog when the "Generate" button is clicked '''

        # Read the parameters directly from the dialog
        startPercent = int(self._dialog.property('startPercent'))
        endPercent = int(self._dialog.property('endPercent'))
        percentChange = int(self._dialog.property('percentChange'))
        towerDescription = self._dialog.property('towerDescription')

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight); # Round up
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
        startPercent = int(self._dialog.property('startPercent'))
        percentChange = int(self._dialog.property('percentChange'))
        displayOnLcd = bool(self._dialog.property('displayOnLcd'))

        # Call the post-processing script
        gcode = FanTower_PostProcessing.execute(gcode, startPercent, percentChange, displayOnLcd, self._sectionLayers, self._baseLayers)

        return gcode
