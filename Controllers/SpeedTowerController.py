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
from ..Postprocessing import SpeedTower_PostProcessing



class SpeedTowerController(QObject):
    _openScadFilename = 'speedtower.scad'
    _qmlFilename = 'SpeedTowerDialog.qml'

    _towerTypesModel = [
        {'value': 'Speed', 'label': 'SPEED'}, 
        {'value': 'Acceleration', 'label': 'ACCELERATION'}, 
        {'value': 'Jerk', 'label': 'JERK'}, 
        {'value': 'Junction', 'label': 'JUNCTION'}, 
        {'value': 'Marlin Linear', 'label': 'MARLIN LINEAR'}, 
        {'value': 'RepRap Pressure', 'label': 'REPRAP PRESSURE'},
    ]

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0

    _presetTables = {
        'Speed 20-100': {
            'filename': 'speedtower 20-100.stl',
            'start value': 20,
            'change value': 20,
            'tower type': 'Speed'
        },

        'Speed 50-150': {
            'filename': 'speedtower 50-150.stl',
            'start value': 50,
            'change value': 150,
            'tower type': 'Speed'
        },

        'Speed 100-200': {
            'filename': 'speedtower 100-200.stl',
            'start value': 100,
            'change value': 200,
            'tower type': 'Speed'
        },
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__()

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._guiPath = guiPath
        self._stlPath = stlPath

        self._startValue = 0
        self._valueChange = 0
        self._baseLayers = 0
        self._sectionLayers = 0



    @staticmethod
    def getPresetNames()->list:
        return list(SpeedTowerController._presetTables.keys())



    _cachedSettingsDialog = None

    @property
    def _settingsDialog(self)->QObject:
        ''' Lazy instantiation of this tower's settings dialog '''
        if self._cachedSettingsDialog is None:
            qmlFilePath = os.path.join(self._guiPath, self._qmlFilename)
            self._cachedSettingsDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedSettingsDialog



    # The available tower types
    @pyqtProperty(list)
    def towerTypesModel(self):
        return self._towerTypesModel



    # The speed tower type 
    _towerType = _towerTypesModel[0]['value']

    towerTypeChanged = pyqtSignal()

    def setTowerType(self, value)->None:
        self._towerType = value
        self.towerTypeChanged.emit()

    @pyqtProperty(str, notify=towerTypeChanged, fset=setTowerType)
    def towerType(self)->str:
        return self._towerType



    # The starting speed value for the tower
    _startSpeedStr = '20'

    startSpeedStrChanged = pyqtSignal()
    
    def setStartSpeedStr(self, value)->None:
        self._startSpeedStr = value
        self.startSpeedStrChanged.emit()

    @pyqtProperty(str, notify=startSpeedStrChanged, fset=setStartSpeedStr)
    def startSpeedStr(self)->str:
        return self._startSpeedStr



    # The ending speed value for the tower
    _endSpeedStr = '100'

    endSpeedStrChanged = pyqtSignal()
    
    def setEndSpeedStr(self, value)->None:
        self._endSpeedStr = value
        self.endSpeedStrChanged.emit()

    @pyqtProperty(str, notify=endSpeedStrChanged, fset=setEndSpeedStr)
    def endSpeedStr(self)->str:
        return self._endSpeedStr



    # The amount to change the speed between tower sections
    _speedChangeStr = '20'

    speedChangeStrChanged = pyqtSignal()
    
    def setSpeedChangeStr(self, value)->None:
        self._speedChangeStr = value
        self.speedChangeStrChanged.emit()

    @pyqtProperty(str, notify=speedChangeStrChanged, fset=setSpeedChangeStr)
    def speedChangeStr(self)->str:
        return self._speedChangeStr



    # The label to add to the tower
    _towerLabelStr = _towerTypesModel[0]['label']

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The temperature label to add to the tower
    _temperatureLabelStr = ''

    temperatureLabelStrChanged = pyqtSignal()
    
    def setTemperatureLabelStr(self, value)->None:
        self._temperatureLabelStr = value
        self.temperatureLabelStrChanged.emit()

    @pyqtProperty(str, notify=temperatureLabelStrChanged, fset=setTemperatureLabelStr)
    def temperatureLabelStr(self)->str:
        return self._temperatureLabelStr



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            # Query the current printing temperature
            printTemperature = Application.getInstance().getGlobalContainerStack().getProperty('material_print_temperature', 'value')
            self.setTemperatureLabelStr(f'{printTemperature}\u00b0')

            self._settingsDialog.show()



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetTables[presetName]
        except KeyError:
            Logger.log('e', f'A SpeedTower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's starting speed
        try:
            self._startValue = presetTable['start value']
        except KeyError:
            Logger.log('e', f'The "start value" for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's speed change value
        try:
            self._valueChange = presetTable['change value']
        except KeyError:
            Logger.log('e', f'The "change value" for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's tower type value
        try:
            self._towerType = presetTable['tower type']
        except KeyError:
            Logger.log('e', f'The "tower type" for SpeedTower preset table "{presetName}" has not been defined')
            return

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Speed Tower ({self._towerType}) {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Read the parameters directly from the dialog
        startSpeed = float(self.startSpeedStr)
        endSpeed = float(self.endSpeedStr)
        speedChange = float(self.speedChangeStr)
        towerLabel = self.towerLabelStr
        temperatureLabel = self.temperatureLabelStr

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

        # Record the tower settings that will be needed for post-processing
        self._startValue = startSpeed
        self._valueChange = speedChange

        # Compile the parameters to send to OpenSCAD
        openScadParameters = {}
        openScadParameters ['Starting_Value'] = startSpeed
        openScadParameters ['Ending_Value'] = endSpeed
        openScadParameters ['Value_Change'] = speedChange
        openScadParameters ['Base_Height'] = baseHeight
        openScadParameters ['Section_Height'] = sectionHeight
        openScadParameters ['Tower_Label'] = towerLabel
        openScadParameters ['Temperature_Label'] = temperatureLabel

        # Determine the tower name
        towerName = f'Auto-Generated Speed Tower ({self._towerType}) {startSpeed}-{endSpeed}x{speedChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    # This function is called by the main script when it's time to post-process the tower model
    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''

        # Call the post-processing script
        gcode = SpeedTower_PostProcessing.execute(gcode, self._startValue, self._valueChange, self._sectionLayers, self._baseLayers, self._towerType)

        return gcode
