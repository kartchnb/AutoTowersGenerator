import os
import math

from PyQt5.QtCore import QObject, pyqtSlot

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger

# Import the script that does the actual post-processing
from .scripts import TempTower_PostProcessing



class TempTowerController(QObject):
    _openScadFilename = 'temptower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0

    _presets = {
        'ABS' : 
        {
            'startTemp' : 250,
            'endTemp' : 210,
            'tempChange' : -5,
            'materialLabel': 'ABS',
            'towerDescription': '',
            'displayOnLcd': True,
        },

        'PETG' : 
        {
            'startTemp' : 260,
            'endTemp' : 230,
            'tempChange' : -5,
            'materialLabel': 'PETG',
            'towerDescription': '',
            'displayOnLcd': True,
        },

        'PLA' : 
        {
            'startTemp' : 220,
            'endTemp' : 180,
            'tempChange' : -5,
            'materialLabel': 'PLA',
            'towerDescription': '',
            'displayOnLcd': True,
        },

        'PLA+' :
        {
            'startTemp' : 230,
            'endTemp' : 200,
            'tempChange' : -5,
            'materialLabel': 'PLA+',
            'towerDescription': '',
            'displayOnLcd': True,
        },

        'TPU' : 
        {
            'startTemp' : 210,
            'endTemp' : 170,
            'tempChange' : -5,
            'materialLabel': 'TPU',
            'towerDescription': '',
            'displayOnLcd': True,
        },
    }



    def __init__(self, pluginPath, modelCallback):
        QObject.__init__(self)

        self._modelCallback = modelCallback

        # Prepare the settings dialog
        qml_file_path = os.path.join(pluginPath, 'gui', 'TempTowerDialog.qml')
        self._dialog = CuraApplication.getInstance().createQmlComponent(qml_file_path, {'manager': self})

        # Set up initial setting values
        self.loadPreset(self._presets['PLA'])

        self._baseLayers = 0
        self._sectionLayers = 0



    def generate(self, presetName):
        try:
            # If the preset name is valid, load it and generate the temperature tower without showing the dialog
            preset = self._presets[presetName]
            self.loadPreset(preset)
            self.dialogAccepted()
        except KeyError:
            # If the preset name isn't defined, show the dialog to let the user configure the tower
            self._dialog.show()



    # Load values from a preset
    @pyqtSlot()
    def loadPreset(self, preset):
        # Assign the value of each parameter in the preset
        for parameter in preset.keys():
            value = preset[parameter]
            self._dialog.setProperty(parameter, value)



    # This function is called when the "Generate" button on the temp tower settings dialog is clicked
    @pyqtSlot()
    def dialogAccepted(self):
        # Read the parameters directly from the dialog
        startTemp = int(self._dialog.property('startTemp'))
        endTemp = int(self._dialog.property('endTemp'))
        tempChange = int(self._dialog.property('tempChange'))
        materialLabel = self._dialog.property('materialLabel')
        towerDescription = self._dialog.property('towerDescription')

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        baseHeight = self._baseLayers * layerHeight

        # Correct the section height to ensure an integer number of layers per section
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up
        sectionHeight = self._sectionLayers * layerHeight

        # Ensure the change amount has the correct sign
        if endTemp >= startTemp:
            tempChange = abs(tempChange)
        else:
            tempChange = -abs(tempChange)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startTemp
        openScadParameters ['Ending_Value'] = endTemp
        openScadParameters ['Value_Change'] = tempChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = materialLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Send the filename and parameters to the model callback
        self._modelCallback(self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode):
        # Read the parameters from the dialog
        startTemp = int(self._dialog.property('startTemp'))
        tempChange = int(self._dialog.property('tempChange'))

        # Call the post-processing script
        gcode = TempTower_PostProcessing.execute(gcode, startTemp, tempChange, self._sectionLayers, self._baseLayers)

        return gcode
