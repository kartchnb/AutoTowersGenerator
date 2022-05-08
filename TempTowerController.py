import os
import math

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

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
            'startTemp' : '250',
            'endTemp' : '210',
            'tempChange' : '-5',
            'materialLabel': 'ABS',
            'towerDescription': '',
        },

        'PETG' : 
        {
            'startTemp' : '260',
            'endTemp' : '230',
            'tempChange' : '-5',
            'materialLabel': 'PETG',
            'towerDescription': '',
        },

        'PLA' : 
        {
            'startTemp' : '220',
            'endTemp' : '180',
            'tempChange' : '-5',
            'materialLabel': 'PLA',
            'towerDescription': '',
        },

        'PLA+' :
        {
            'startTemp' : '230',
            'endTemp' : '200',
            'tempChange' : '-5',
            'materialLabel': 'PLA+',
            'towerDescription': '',
        },

        'TPU' : 
        {
            'startTemp' : '210',
            'endTemp' : '170',
            'tempChange' : '-5',
            'materialLabel': 'TPU',
            'towerDescription': '',
        },
    }



    def __init__(self, pluginPath, modelCallback):
        QObject.__init__(self)

        self._modelCallback = modelCallback

        # Prepare the settings dialog
        qml_file_path = os.path.join(pluginPath, 'gui', 'TempTowerDialog.qml')
        self._dialog = CuraApplication.getInstance().createQmlComponent(qml_file_path, {'manager': self})

        self._baseLayers = 0
        self._sectionLayers = 0



    # The starting temperature value for the tower
    _startTemperatureStr = '220'

    startTemperatureStrChanged = pyqtSignal()
    
    def setStartTemperatureStr(self, value):
        self._startTemperatureStr = value
        self.startTemperatureStrChanged.emit()

    @pyqtProperty(str, notify=startTemperatureStrChanged, fset=setStartTemperatureStr)
    def startTemperatureStr(self) -> str:
        return self._startTemperatureStr



    # The ending temperature value for the tower
    _endTemperatureStr = '180'

    endTemperatureStrChanged = pyqtSignal()
    
    def setEndTemperatureStr(self, value):
        self._endTemperatureStr = value
        self.endTemperatureStrChanged.emit()

    @pyqtProperty(str, notify=endTemperatureStrChanged, fset=setEndTemperatureStr)
    def endTemperatureStr(self) -> str:
        return self._endTemperatureStr



    # The amount to change the temperature between tower sections
    _temperatureChangeStr = '-5'

    temperatureChangeStrChanged = pyqtSignal()
    
    def setTemperatureChangeStr(self, value):
        self._temperatureChangeStr = value
        self.temperatureChangeStrChanged.emit()

    @pyqtProperty(str, notify=temperatureChangeStrChanged, fset=setTemperatureChangeStr)
    def temperatureChangeStr(self) -> str:
        return self._temperatureChangeStr



    # The material label to add to the tower
    _materialLabelStr = ''

    materialLabelStrChanged = pyqtSignal()
    
    def setMaterialLabelStr(self, value):
        self._materialLabelStr = value
        self.materialLabelStrChanged.emit()

    @pyqtProperty(str, notify=materialLabelStrChanged, fset=setMaterialLabelStr)
    def materialLabelStr(self) -> str:
        return self._materialLabelStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = ''

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value):
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self) -> str:
        return self._towerDescriptionStr



    def generate(self, presetName):
        try:
            # If the preset name is valid, load it and generate the temperature tower without showing the dialog
            preset = self._presets[presetName]
            self.loadPreset(preset)
        except KeyError:
            # If the preset name isn't defined, ignore the error and allow the user to customize the tower
            pass

        self._dialog.show()



    # Load values from a preset
    @pyqtSlot()
    def loadPreset(self, preset):
        self.setStartTemperatureStr(preset['startTemp'])
        self.setEndTemperatureStr(preset['endTemp'])
        self.setTemperatureChangeStr(preset['tempChange'])
        self.setMaterialLabelStr(preset['materialLabel'])
        self.setTowerDescriptionStr(preset['towerDescription'])



    # This function is called when the "Generate" button on the temp tower settings dialog is clicked
    @pyqtSlot()
    def dialogAccepted(self):
        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Correct the base height to ensure an integer number of layers in the base
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        baseHeight = self._baseLayers * layerHeight

        # Correct the section height to ensure an integer number of layers per section
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up
        sectionHeight = self._sectionLayers * layerHeight

        # Determine the parameters for the tower
        startTemperature = float(self.startTemperatureStr)
        endTemperature = float(self.endTemperatureStr)
        temperatureChange = float(self.temperatureChangeStr)
        materialLabel = self.materialLabelStr
        towerDescription = self.towerDescriptionStr

        # Ensure the change amount has the correct sign
        if endTemperature >= startTemperature:
            temperatureChange = abs(temperatureChange)
        else:
            temperatureChange = -abs(temperatureChange)

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startTemperature
        openScadParameters ['Ending_Value'] = endTemperature
        openScadParameters ['Value_Change'] = temperatureChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Column_Label'] = materialLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Send the filename and parameters to the model callback
        self._modelCallback(self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode):
        # Read the parameters from the dialog
        startTemperature = float(self.startTemperatureStr)
        temperatureChange = float(self.temperatureChangeStr)

        # Call the post-processing script
        gcode = TempTower_PostProcessing.execute(gcode, startTemperature, temperatureChange, self._sectionLayers, self._baseLayers)

        return gcode
