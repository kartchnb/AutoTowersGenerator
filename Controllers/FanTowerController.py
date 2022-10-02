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
from ..Postprocessing import FanTower_PostProcessing



class FanTowerController(QObject):
    _openScadFilename = 'temptower.scad'
    _qmlFilename = 'FanTowerDialog.qml'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0

    _presetTables = {
        '0-100': {
            'filename': 'fantower 0-100.stl',
            'start value': 0,
            'change value': 20,
        },
    }


    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        super().__init__()

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._guiPath = guiPath
        self._stlPath = stlPath

        self._startPercent = 0
        self._percentChange = 0
        self._baseLayers = 0
        self._sectionLayers = 0



    @staticmethod
    def getPresetNames()->list:
        return list(FanTowerController._presetTables.keys())


    _cachedSettingsDialog = None

    @property
    def _settingsDialog(self)->QObject:
        ''' Lazy instantiation of this tower's settings dialog '''
        if self._cachedSettingsDialog is None:
            qmlFilePath = os.path.join(self._guiPath, self._qmlFilename)
            self._cachedSettingsDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedSettingsDialog



    # The starting percentage value for the tower
    _startPercentStr = '0'

    startPercentStrChanged = pyqtSignal()
    
    def setStartPercentStr(self, value)->None:
        self._startPercentStr = value
        self.startPercentStrChanged.emit()

    @pyqtProperty(str, notify=startPercentStrChanged, fset=setStartPercentStr)
    def startPercentStr(self)->str:
        return self._startPercentStr



    # The ending percentage value for the tower
    _endPercentStr = '100'

    endPercentStrChanged = pyqtSignal()
    
    def setEndPercentStr(self, value)->None:
        self._endPercentStr = value
        self.endPercentStrChanged.emit()

    @pyqtProperty(str, notify=endPercentStrChanged, fset=setEndPercentStr)
    def endPercentStr(self)->str:
        return self._endPercentStr



    # The amount to change the percentage between tower sections
    _percentChangeStr = '20'

    percentChangeStrChanged = pyqtSignal()
    
    def setPercentChangeStr(self, value)->None:
        self._percentChangeStr = value
        self.percentChangeStrChanged.emit()

    @pyqtProperty(str, notify=percentChangeStrChanged, fset=setPercentChangeStr)
    def percentChangeStr(self)->str:
        return self._percentChangeStr



    # The label to carve at the bottom of the tower
    _towerLabelStr = ''

    towerLabelStrChanged = pyqtSignal()
    
    def setTowerLabelStr(self, value)->None:
        self._towerLabelStr = value
        self.towerLabelStrChanged.emit()

    @pyqtProperty(str, notify=towerLabelStrChanged, fset=setTowerLabelStr)
    def towerLabelStr(self)->str:
        return self._towerLabelStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = 'FAN'

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value)->None:
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self)->str:
        return self._towerDescriptionStr



    # Determine if the same fan value is maintained while bridges are being printed
    _maintainBridgeValue = False

    maintainBridgeValueChanged = pyqtSignal()

    def setMaintainBridgeValue(self, value)->None:
        self._maintainBridgeValue = value
        self.maintainBridgeValueChanged.emit()

    @pyqtProperty(bool, notify=maintainBridgeValueChanged, fset=setMaintainBridgeValue)
    def maintainBridgeValue(self)->bool:
        return self._maintainBridgeValue



    def settingsAreCompatible(self)->str:
        ''' Check whether Cura's settings are compatible with this tower '''

        containerStack = Application.getInstance().getGlobalContainerStack()

        # The tower cannot be generated if supports are enabled
        supportEnabled = containerStack.getProperty('support_enable', 'value')
        if supportEnabled:
            return 'Cannot generate a Fan Tower with supports enabled.\nDisable supports and try again.'

        # The tower cannot be generated if adaptive layers are enabled
        adaptive_layers_enabled = containerStack.getProperty('adaptive_layer_height_enabled', 'value')
        if adaptive_layers_enabled:
            return 'Cannot generate a Fan Tower with adaptive layers enabled.\nDisable adaptive layers and try again.'

        return ''



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self._settingsDialog.show()



    def _loadPreset(self, presetName)->None:
        ''' Load a preset tower '''
        # Load the preset table
        try:
            presetTable = self._presetTables[presetName]
        except KeyError:
            Logger.log('e', f'A FanTower preset named "{presetName}" was requested, but has not been defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for FanTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's starting fan percent
        try:
            self._startPercent = presetTable['start value']
        except KeyError:
            Logger.log('e', f'The "start value" for FanTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's fan change percent
        try:
            self._percentChange = presetTable['change value']
        except KeyError:
            Logger.log('e', f'The "change value" for FanTower preset table "{presetName}" has not been defined')
            return

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Determine the tower name
        towerName = f'Preset Fan Tower {presetName}'

        # Use the callback to load the preset STL file
        self._loadStlCallback(towerName, stlFilePath, self.postProcess)



    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
        # Read the parameters directly from the dialog
        startPercent = float(self.startPercentStr)
        endPercent = float(self.endPercentStr)
        percentChange = float(self.percentChangeStr)
        towerLabel = self.towerLabelStr
        towerDescription = self.towerDescriptionStr

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Record the tower settings that will be needed for post-processing
        self._startPercent = startPercent
        self._percentChange = percentChange

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
        openScadParameters ['Column_Label'] = towerLabel
        openScadParameters ['Tower_Label'] = towerDescription

        # Determine the tower name
        towerName = f'Auto-Generated Fan Tower {startPercent}-{endPercent}x{percentChange}'

        # Send the filename and parameters to the model callback
        self._generateAndLoadStlCallback(towerName, self._openScadFilename, openScadParameters, self.postProcess)



    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        
        # Call the post-processing script
        gcode = FanTower_PostProcessing.execute(gcode, self._startPercent, self._percentChange, self._sectionLayers, self._baseLayers, self.maintainBridgeValue)

        return gcode
