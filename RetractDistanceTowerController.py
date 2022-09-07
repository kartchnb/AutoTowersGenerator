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



class RetractDistanceTowerController(QObject):
    _openScadFilename = 'retracttower.scad'

    _nominalBaseHeight = 0.8
    _nominalSectionHeight = 8.0

    _presetTables = {
        '1-6': {
            'filename': 'retractdistancetower-1-6.stl',
            'start value': 1,
            'change value': 1,
        },

        '4-9': {
            'filename': 'retractdistancetower-4-9.stl',
            'start value': 4,
            'change value': 1,
        },

        '7-12': {
            'filename': 'retractdistancetower-7-12.stl',
            'start value': 7,
            'change value': 1,
        },
    }



    def __init__(self, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback):
        QObject.__init__(self)

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._guiPath = guiPath
        self._stlPath = stlPath

        self._startDistance = 0
        self._distanceChange = 0
        self._baseLayers = 0
        self._sectionLayers = 0



    _cachedSettingsDialog = None

    @property
    def _settingsDialog(self)->QObject:
        ''' Lazy instantiation of this tower's settings dialog '''
        if self._cachedSettingsDialog is None:
            qmlFilePath = os.path.join(self._guiPath, 'RetractDistanceTowerDialog.qml')
            self._cachedSettingsDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedSettingsDialog



    # The starting retraction distance
    _startDistanceStr = '1'

    startDistanceStrChanged = pyqtSignal()

    def setStartDistanceStr(self, value)->None:
        self._startDistanceStr = value
        self.startDistanceStrChanged.emit()

    @pyqtProperty(str, notify=startDistanceStrChanged, fset=setStartDistanceStr)
    def startDistanceStr(self)->str:
        return self._startDistanceStr



    # The ending retraction distance
    _endDistanceStr = '6'
    
    endDistanceStrChanged = pyqtSignal()

    def setEndDistanceStr(self, value)->None:
        self._endDistanceStr = value
        self.endDistanceStrChanged.emit()

    @pyqtProperty(str, notify=endDistanceStrChanged, fset=setEndDistanceStr)
    def endDistanceStr(self)->str:
        return self._endDistanceStr



    # The amount to change the retraction distance between tower sections
    _distanceChangeStr = '1'

    distanceChangeStrChanged = pyqtSignal()

    def setDistanceChange(self, value)->None:
        self._distanceChangeStr = value
        self.distanceChangeStrChanged.emit()

    @pyqtProperty(str, notify=distanceChangeStrChanged, fset=setDistanceChange)
    def distanceChangeStr(self)->str:
        return self._distanceChangeStr



    # The description to carve up the side of the tower
    _towerDescriptionStr = ''

    towerDescriptionStrChanged = pyqtSignal()
    
    def setTowerDescriptionStr(self, value)->None:
        self._towerDescriptionStr = value
        self.towerDescriptionStrChanged.emit()

    @pyqtProperty(str, notify=towerDescriptionStrChanged, fset=setTowerDescriptionStr)
    def towerDescriptionStr(self)->str:
        return self._towerDescriptionStr



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
            Logger.log('e', f'A RetractDistanceTower preset named "{presetName}" was requested, but has not been correctly defined')
            return

        # Load the preset's file name
        try:
            stlFileName = presetTable['filename']
        except KeyError:
            Logger.log('e', f'The "filename" entry for RetractDistanceTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's starting fan percent
        try:
            self._startDistance = presetTable['start value']
        except KeyError:
            Logger.log('e', f'The "start value" for RetractDistanceTower preset table "{presetName}" has not been defined')
            return

        # Load the preset's fan change percent
        try:
            self._distanceChange = presetTable['change value']
        except KeyError:
            Logger.log('e', f'The "change value" for RetractDistanceTower preset table "{presetName}" has not been defined')
            return

        # Query the current layer height
        layerHeight = Application.getInstance().getGlobalContainerStack().getProperty("layer_height", "value")

        # Calculate the number of layers in the base and each section of the tower
        self._baseLayers = math.ceil(self._nominalBaseHeight / layerHeight) # Round up
        self._sectionLayers = math.ceil(self._nominalSectionHeight / layerHeight) # Round up

        # Determine the file path of the preset
        stlFilePath = os.path.join(self._stlPath, stlFileName)

        # Use the callback to load the preset STL file
        self._loadStlCallback(stlFilePath, self.postProcess)



    # This function is called when the 'Generate' button on the temp tower settings dialog is clicked
    @pyqtSlot()
    def dialogAccepted(self)->None:
        ''' This method is called by the dialog when the "Generate" button is clicked '''
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

        # Record the tower settings that will be needed for post-processing
        self._startDistance = startDistance
        self._distanceChange = distanceChange

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
        self._generateAndLoadStlCallback(self._openScadFilename, openScadParameters, self.postProcess)



    # This code was modified from the RetractTower.py post-processing script
    # provided as part of 5axes' CalibrationShapes plugin
    def postProcess(self, gcode)->list:
        ''' This method is called to post-process the gcode before it is sent to the printer or disk '''
        # Determine the parameters for the tower
        startDistance = float(self.startDistanceStr)
        distanceChange = float(self.distanceChangeStr)

        # Call the post-processing script
        gcode = RetractTower_PostProcessing.execute(gcode, self._startDistance, self._distanceChange, self._sectionLayers, self._baseLayers, 'distance')

        return gcode
