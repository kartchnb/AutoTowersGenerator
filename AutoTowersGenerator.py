import json
import os
import tempfile

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
    PYQT_VERSION = 5

from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Message import Message
from UM.PluginRegistry import PluginRegistry

from . import MeshImporter
from .OpenScadInterface import OpenScadInterface
from .OpenScadJob import OpenScadJob

from .Controllers.FanTowerController import FanTowerController
from .Controllers.FlowTowerController import FlowTowerController
from .Controllers.RetractTowerController import RetractTowerController
from .Controllers.SpeedTowerController import SpeedTowerController
from .Controllers.TempTowerController import TempTowerController



class AutoTowersGenerator(QObject, Extension):
    _pluginName = 'AutoTowersGenerator'

    _gcodeProcessedMarker = ';Post-processed by the AutoTowersGenerator plugin'



    def __init__(self):
        QObject.__init__(self)
        Extension.__init__(self)

        # Initialize the plugin settings
        self._pluginSettings = {}

        # Keep track of the post-processing callback and the node added by the OpenSCAD import
        self._towerControllerPostProcessingCallback = None
        self._importedNode = None

        # Keep track of whether a model has been generated and is in the scene
        self._autoTowerGenerated = False
        self._autoTowerOperation = None

        # Update the view when the main window is changed so the "remove" button is always visible when enabled
        # Not sure if this is needed
        CuraApplication.getInstance().mainWindowChanged.connect(self._displayRemoveAutoTowerButton)

        # Finish initializing the plugin after Cura is fully ready
        Application.getInstance().pluginsLoaded.connect(self._onPluginsLoadedCallback)



    @property
    def _pluginPath(self)->str:
        ''' Returns the path to the plugin directory '''

        return PluginRegistry.getInstance().getPluginPath(self.getPluginId())



    @property
    def _openScadSourcePath(self)->str:
        ''' Returns the path to the OpenSCAD source models'''

        return os.path.join(self._pluginPath, 'Resources', 'OpenScad')


    
    @property
    def _qmlPath(self)->str:
        ''' Returns the path to where the QML dialog files directory '''

        return os.path.join(self._pluginPath, 'Resources', 'QML', f'QT{PYQT_VERSION}')



    @property
    def _stlPath(self)->str:
        ''' Returns the path where STL files are stored '''

        return os.path.join(self._pluginPath, 'Resources', 'STL')



    @property
    def _pluginSettingsFilePath(self)->str:
        ''' Returns the path of the plugins settings file '''

        return os.path.join(self._pluginPath, 'Resources', 'settings.json')



    _cachedRemoveModelsButton = None

    @property
    def _removeAutoTowerButton(self)->QObject:
        ''' Returns the button used to remove the Auto Tower from the scene '''

        if self._cachedRemoveModelsButton is None:
            self._cachedRemoveModelsButton = self._createDialog('RemoveModelsButton.qml')
        return self._cachedRemoveModelsButton



    _cachedPluginSettingsDialog = None

    @property
    def _pluginSettingsDialog(self)->QObject:
        ''' Returns the settings dialog '''

        if self._cachedPluginSettingsDialog is None:
            self._cachedPluginSettingsDialog = self._createDialog('PluginSettingsDialog.qml')
        return self._cachedPluginSettingsDialog



    _cachedWaitDialog = None

    @property
    def _waitDialog(self)->QObject:
        ''' Returns the dialog used to tell the user that generating a model may take a long time '''

        if self._cachedWaitDialog is None:
            self._cachedWaitDialog = self._createDialog('WaitDialog.qml')
        return self._cachedWaitDialog



    _cachedFanTowerController = None

    @property
    def _fanTowerController(self)->FanTowerController:
        ''' Returns the object used to create a Fan Tower '''
        
        if self._cachedFanTowerController is None:
            self._cachedFanTowerController = FanTowerController(self._qmlPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedFanTowerController



    _cachedFlowTowerController = None

    @property
    def _flowTowerController(self)->FlowTowerController:
        ''' Returns the object used to create a Flow Tower '''
        
        if self._cachedFlowTowerController is None:
            self._cachedFlowTowerController = FlowTowerController(self._qmlPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedFlowTowerController



    _cachedRetractTowerController = None

    @property
    def _retractTowerController(self)->RetractTowerController:
        ''' Returns the object used to create a Retraction Distance Tower '''

        if self._cachedRetractTowerController is None:
            self._cachedRetractTowerController = RetractTowerController(self._qmlPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedRetractTowerController



    _cachedSpeedTowerController = None

    @property
    def _speedTowerController(self)->SpeedTowerController:
        ''' Returns the object used to create a Speed Tower '''

        if self._cachedSpeedTowerController is None:
            self._cachedSpeedTowerController = SpeedTowerController(self._qmlPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedSpeedTowerController



    _cachedTempTowerController = None

    @property
    def _tempTowerController(self)->TempTowerController:
        ''' Returns the object used to create a Temperature Tower '''

        if self._cachedTempTowerController is None:
            self._cachedTempTowerController = TempTowerController(self._qmlPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedTempTowerController



    _cachedOpenScadInterface = None
    @property
    def _openScadInterface(self)->OpenScadInterface:
        ''' Provides lazy instantiation of the OpenScad interface '''

        if self._cachedOpenScadInterface is None:
            self._cachedOpenScadInterface = OpenScadInterface()

        return self._cachedOpenScadInterface



    autoTowerGeneratedChanged = pyqtSignal()
    @pyqtProperty(bool, notify=autoTowerGeneratedChanged)
    def autoTowerGenerated(self)->bool:
        ''' Used to show or hide the button for removing the generated Auto Tower '''

        return self._autoTowerGenerated



    _openScadPathSetting = ''

    _openScadPathSettingChanged = pyqtSignal()
    
    def setOpenScadPathSetting(self, value)->None:
        self._openScadPathSetting = value
        self._openScadPathSettingChanged.emit()

    @pyqtProperty(str, notify=_openScadPathSettingChanged, fset=setOpenScadPathSetting)
    def openScadPathSetting(self)->str:
        return self._openScadPathSetting



    @pyqtSlot()
    def removeButtonClicked(self)->None:
        ''' Called when the remove button is clicked to remove the generated Auto Tower from the scene'''

        # Remove the tower
        self._removeAutoTower()

        # Notify the user that the Auto Tower has been removed
        Message('The Auto Tower model and its associated post-processing has been removed', title=self._pluginName).show()



    @pyqtSlot()
    def pluginSettingsModified(self)->None:
        ''' Saves plugin settings to a json file so they persist between sessions '''

        # Send the new OpenScad path to the OpenScad Interface
        self._openScadInterface.SetOpenScadPath(self.openScadPathSetting)

        # Warn the user if the OpenScad path is not valid
        if not self._openScadInterface.OpenScadPathValid:
            message = f'The OpenScad path "{self._openScadInterface.OpenScadPath}" is not valid'
            Message(message, title=self._pluginName).show()

        # Create a settings dictionary to dump to the settings file
        pluginSettings = {
            'openscad path': self.openScadPathSetting
        }

        # Save the settings to the settings file
        with open(self._pluginSettingsFilePath, 'w') as settingsFile:
            json.dump(pluginSettings, settingsFile)



    def _loadPluginSettings(self)->None:
        ''' Load plugin settings from the settings.json file  '''

        try:
            # Load settings from the settings file, if it exists
            with open(self._pluginSettingsFilePath, 'r') as settingsFile:
                pluginSettings = json.load(settingsFile)

            # Forward the OpenScad path to the OpenScadInterface object
            self.setOpenScadPathSetting(pluginSettings['openscad path'])
            self._openScadInterface.SetOpenScadPath(self.openScadPathSetting)

        except (FileNotFoundError, KeyError):
            pass



    def _initializeMenu(self)->None:
        # Add a menu for this plugin
        self.setMenuName('Auto Towers')

        dividerCount = 0;

        # Add menu entries for fan towers
        for presetName in FanTowerController.getPresetNames():
            self.addMenuItem(f'Fan Tower ({presetName})', lambda presetName=presetName: self._generateAutoTower(self._fanTowerController, presetName))
        self.addMenuItem('Fan Tower (Custom)', lambda: self._generateAutoTower(self._fanTowerController))

        # Add menu entries for flow towers
        self.addMenuItem(' ' * dividerCount, lambda: None)
        dividerCount += 1
        for presetName in FlowTowerController.getPresetNames():
            self.addMenuItem(f'Flow Tower ({presetName})', lambda presetName=presetName: self._generateAutoTower(self._flowTowerController, presetName))
        self.addMenuItem('Flow Tower (Custom)', lambda: self._generateAutoTower(self._flowTowerController))
        
        # Add menu entries for retraction towers
        self.addMenuItem(' ' * dividerCount, lambda: None)
        dividerCount += 1
        for presetName in RetractTowerController.getPresetNames():
            self.addMenuItem(f'Retraction Tower ({presetName})', lambda presetName=presetName: self._generateAutoTower(self._retractTowerController, presetName))
        self.addMenuItem('Retraction Tower (Custom)', lambda: self._generateAutoTower(self._retractTowerController))
        
        # Add menu entries for speed towers
        self.addMenuItem(' ' * dividerCount, lambda: None)
        dividerCount += 1
        for presetName in SpeedTowerController.getPresetNames():
            self.addMenuItem(f'Speed Tower ({presetName})', lambda presetName=presetName: self._generateAutoTower(self._speedTowerController, presetName))
        self.addMenuItem('Speed Tower (Custom)', lambda: self._generateAutoTower(self._speedTowerController))

        # Add menu entries for temperature towers
        self.addMenuItem(' ' * dividerCount, lambda: None)
        dividerCount += 1
        for presetName in TempTowerController.getPresetNames():
            self.addMenuItem(f'Temperature Tower ({presetName})', lambda presetName=presetName: self._generateAutoTower(self._tempTowerController, presetName))
        self.addMenuItem('Temperature Tower (Custom)', lambda: self._generateAutoTower(self._tempTowerController))

        # Add a menu item for modifying plugin settings
        self.addMenuItem(' ' * dividerCount, lambda: None)
        dividerCount += 1
        self.addMenuItem('Settings', lambda: self._displayPluginSettingsDialog())



    def _generateAutoTower(self, towerController, presetName=''):
        ''' Verifies print settings and generates the requested auto tower '''

        # Allow the tower controller to check Cura's settings to ensure it can be generated
        errorMessage = towerController.settingsAreCompatible()
        if errorMessage != '':
            Message(errorMessage, title=self._pluginName).show()
            return

        # Custom auto towers cannot be generated unless OpenScad is correctly installed and configured
        openscad_path_is_valid = self._openScadInterface.OpenScadPathValid
        if presetName == '' and not openscad_path_is_valid:
            Logger.log('d', f'The openScad path "{self._openScadInterface.OpenScadPath}" is invalid')
            message = 'This functionality relies on OpenSCAD, which is not installed or configured correctly\n'
            message += 'Please ensure OpenSCAD is installed (openscad.org) and that its path has been set correctly in this plugin\'s settings\n'
            Message(message, title=self._pluginName).show()
            return

        towerController.generate(presetName)



    def _removeAutoTower(self)->None:
        ''' Removes the generated Auto Tower and post-processing callbacks '''

        # Indicate that there is no longer an Auto Tower in the scene
        self._autoTowerGenerated = False
        self.autoTowerGeneratedChanged.emit()

        # Remove the Auto Tower itself
        self._autoTowerOperation.undo()

        # Remove the post-processing callback
        Application.getInstance().getOutputDeviceManager().writeStarted.disconnect(self._postProcess)
        self._towerControllerPostProcessingCallback = None

        # Clear the job name
        CuraApplication.getInstance().getPrintInformation().setJobName('')

        # Stop listening for machine changes
        try:
            CuraApplication.getInstance().getMachineManager().globalContainerChanged.disconnect(self._onMachineChanged)
        except:
            # Not sure how to handle this yet
            pass

        try:
            CuraApplication.getInstance().getMachineManager().activeMachine.propertyChanged.disconnect(self._onPrintSettingChanged)
        except:
            # Not sure how to handle this yet
            pass



    def _createDialog(self, qml_filename)->QObject:
        ''' Creates a dialog object from a QML file name 
            The QML file is assumed to be in the GUI directory             
            Returns a dialog object, with this object assigned as the "manager" '''

        qml_file_path = os.path.join(self._qmlPath, qml_filename)
        dialog = Application.getInstance().createQmlComponent(qml_file_path, {'manager': self})
        return dialog



    def _displayRemoveAutoTowerButton(self)->None:
        ''' Adds a button to Cura's window to remove the Auto Tower '''

        CuraApplication.getInstance().addAdditionalComponent('saveButton', self._removeAutoTowerButton)



    def _displayPluginSettingsDialog(self)->None:
        ''' Prepares and displays the plugin settings dialog '''

        # Update the OpenScad path from the OpenScad interface
        self.setOpenScadPathSetting(self._openScadInterface.OpenScadPath)

        self._pluginSettingsDialog.show()



    def _onPluginsLoadedCallback(self):
        ''' Called after plugins have been loaded
            Iniializing here means that Cura is fully ready '''

        # Load plugin settings
        self._loadPluginSettings()

        # Add menus
        self._initializeMenu()



    def _loadStlCallback(self, towerName, stlFilePath, postProcessingCallback)->None:
        ''' This callback is called by the tower model controller if a preset tower is requested '''

        # If the file does not exist, display an error message
        if os.path.isfile(stlFilePath) == False:
            errorMessage = f'The STL file "{stlFilePath}" does not exist'
            Logger.log('e', errorMessage)
            Message(errorMessage, title = self._pluginName).show()
            return

        # Import the STL file into the scene
        self._importStl(towerName, stlFilePath, postProcessingCallback)



    def _generateAndLoadStlCallback(self, towerName, openScadFilename, openScadParameters, postProcessingCallback)->None:
        ''' This callback is called by the tower model controller after a tower has been configured to generate an STL model from an OpenSCAD file '''

        # This could take up to a couple of minutes...
        self._waitDialog.show()
        CuraApplication.getInstance().processEvents() # Allow Cura to update itself periodically through this method

        # Remove all models from the scene
        self._autoTowerGenerated = False
        CuraApplication.getInstance().deleteAll()
        CuraApplication.getInstance().processEvents()
        
        # Compile the STL file name
        openScadFilePath = os.path.join(self._openScadSourcePath, openScadFilename)
        stlFilename = 'custom_autotower.stl'
        stlOutputDir = tempfile.TemporaryDirectory()
        stlFilePath = os.path.join(stlOutputDir.name, stlFilename)

        # Generate the STL file
        # Since it can take a while to generate the STL file, do it in a separate thread to allow the GUI to remain responsive
        job = OpenScadJob(self._openScadInterface, openScadFilePath, openScadParameters, stlFilePath)
        job.run()

        # Wait for OpenSCAD to finish
        # This should probably be done by having a function called when the job finishes...
        while (job.isRunning()):
            pass

        # Make sure the STL file was generated
        if os.path.isfile(stlFilePath) == False:
            errorMessage = f'Failed to generate "{stlFilePath}" from "{openScadFilename}":\n{self._openScadInterface.errorMessage}'
            Logger.log('e', errorMessage)
            Message(errorMessage, title=self._pluginName).show()
            self._waitDialog.hide()
            return

        # Import the STL file into the scene
        self._importStl(towerName, stlFilePath, postProcessingCallback)



    def _importStl(self, towerName, stlFilePath, postProcessingCallback)->None:
        ''' Imports an STL file into the scene '''

        # Remove all models from the scene
        self._autoToweradaptive_layers_enabled = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty('adaptive_layer_height_enabled', 'value')
        CuraApplication.getInstance().deleteAll()
        CuraApplication.getInstance().processEvents()

        # Import the STL file into the scene
        self._autoTowerOperation = MeshImporter.ImportMesh(stlFilePath, False)
        CuraApplication.getInstance().processEvents()

        # Register the post-processing callback for this particular tower
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self._postProcess)
        self._towerControllerPostProcessingCallback = postProcessingCallback

        # Register that the Auto Tower has been generated
        self._autoTowerGenerated = True
        self.autoTowerGeneratedChanged.emit()

        # If the machine or applicable print settings are changed, the tower will automatically be removed from the scene
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._onMachineChanged)
        CuraApplication.getInstance().getMachineManager().activeMachine.propertyChanged.connect(self._onPrintSettingChanged)

        # The dialog is no longer needed
        self._waitDialog.hide()

        # Rename the current print job
        CuraApplication.getInstance().getPrintInformation().setJobName(towerName)



    def _onMachineChanged(self)->None:
        ''' Listen for machine changes made after an Auto Tower is generated 
            In this case, the Auto Tower needs to be removed and regenerated '''

        self._removeAutoTower()
        Message('The Auto Tower has been removed because the active machine was changed', title=self._pluginName).show()        



    def _onPrintSettingChanged(self, setting_key, property_name)->None:
        ''' Listen for setting changes made after an Auto Tower is generated '''

        # Remove the tower in response to settings changes
        self._removeAutoTower()
        setting_label = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty(setting_key, 'label')
        Message(f'The Auto Tower has been removed because the Cura setting "{setting_label}" has changed since the tower was generated', title=self._pluginName).show()
                


    def _postProcess(self, output_device)->None:
        ''' This callback is called just before gcode is generated for the model 
            (this happens when the sliced model is sent to the printer or a file '''

        # Retrieve the g-code from the scene
        scene = Application.getInstance().getController().getScene()

        try:
            # Proceed if the g-code is valid
            gcode_dict = getattr(scene, 'gcode_dict')
        except AttributeError:
            # If there is no g-code, there's nothing more to do
            return

        try:
            # Retrieve the g-code for the current build plate
            active_build_plate_id = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
            gcode = gcode_dict[active_build_plate_id]
        except TypeError:
            # If there is no g-code for the current build plate, there's nothing more to do
            return

        # Proceed if the g-code has not already been post-processed
        if self._gcodeProcessedMarker not in gcode[0]:

            # Mark the g-code as having been post-processed
            gcode[0] = gcode[0] + self._gcodeProcessedMarker + '\n'

            # Call the callback to post-process the g-code
            gcode = self._towerControllerPostProcessingCallback(gcode)
