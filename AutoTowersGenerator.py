import hashlib
import json
import os
import platform
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
from . import OpenScadInterface
from . import OpenScadJob

from . import FanTowerController
from . import RetractDistanceTowerController
from . import RetractSpeedTowerController
from . import TempTowerController



class AutoTowersGenerator(QObject, Extension):
    _pluginName = 'AutoTowersGenerator'

    _gcodeProcessedMarker = ';Post-processed by the AutoTowersGenerator plugin'



    def __init__(self):
        QObject.__init__(self)
        Extension.__init__(self)

        # Add menu items for this plugin
        self.setMenuName('Auto Towers')
        self.addMenuItem('Fan Tower (0-100%)', lambda: self._fanTowerController.generate('0-100'))
        self.addMenuItem('Fan Tower (Custom)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._fanTowerController.generate()))
        self.addMenuItem('', lambda: None)
        self.addMenuItem('Retraction Distance Tower (1-6 mm)', lambda: self._retractionDistanceTowerController.generate('1-6'))
        self.addMenuItem('Retraction Distance Tower (4-9 mm)', lambda: self._retractionDistanceTowerController.generate('4-9'))
        self.addMenuItem('Retraction Distance Tower (7-12 mm)', lambda: self._retractionDistanceTowerController.generate('7-12'))
        self.addMenuItem('Retraction Distance Tower (Custom)', lambda: self._retractionDistanceTowerController.generate())
        self.addMenuItem(' ', lambda: None)
        self.addMenuItem('Retraction Speed Tower (10-50 mm/s)', lambda: self._retractionSpeedTowerController.generate('10-50'))
        self.addMenuItem('Retraction Speed Tower (35-75 mm/s)', lambda: self._retractionSpeedTowerController.generate('35-75'))
        self.addMenuItem('Retraction Speed Tower (60-100 mm/s)', lambda: self._retractionSpeedTowerController.generate('60-100'))
        self.addMenuItem('Retraction Speed Tower (Custom)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._retractionSpeedTowerController.generate()))
        self.addMenuItem('  ', lambda: None)
        self.addMenuItem('Temperature Tower (ABA)', lambda: self._tempTowerController.generate('aba'))
        self.addMenuItem('Temperature Tower (ABS)', lambda: self._tempTowerController.generate('abs'))
        self.addMenuItem('Temperature Tower (NYLON)', lambda: self._tempTowerController.generate('nylon'))
        self.addMenuItem('Temperature Tower (PC)', lambda: self._tempTowerController.generate('pc'))
        self.addMenuItem('Temperature Tower (PETG)', lambda: self._tempTowerController.generate('petg'))
        self.addMenuItem('Temperature Tower (PLA)', lambda: self._tempTowerController.generate('pla'))
        self.addMenuItem('Temperature Tower (PLA+)', lambda: self._tempTowerController.generate('pla+'))
        self.addMenuItem('Temperature Tower (TPU)', lambda: self._tempTowerController.generate('tpu'))
        self.addMenuItem('Temperature Tower (Custom)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate()))
        self.addMenuItem('   ', lambda: None)
        self.addMenuItem('Settings', lambda: self._settingsDialog.show())

        # Keep track of the post-processing callback and the node added by the OpenSCAD import
        self._towerControllerPostProcessingCallback = None
        self._importedNode = None

        # Keep track of whether a model has been generated and is in the scene
        self._autoTowerGenerated = False
        self._autoTowerOperation = None

        # Keep track of the layer height that an AutoTower has been generated for
        self._generatedLayerHeight = 0
        self._currentLayerHeight = 0

        # Keep track of the current support enabled setting
        self._currentSupportEnabled = False

        # Update the view when the main window is changed so the "remove" button is always visible when enabled
        # Not sure if this is needed
        CuraApplication.getInstance().mainWindowChanged.connect(self._displayRemoveAutoTowerButton)



    @property
    def _pluginPath(self)->str:
        ''' Returns the path to the plugin directory '''

        return PluginRegistry.getInstance().getPluginPath(self.getPluginId())



    @property
    def _openScadSourcePath(self)->str:
        ''' Returns the path to the OpenSCAD source models'''

        return os.path.join(self._pluginPath, 'openscad')


    
    @property
    def _guiPath(self)->str:
        ''' Returns the path to the GUI files directory '''

        return os.path.join(self._pluginPath, 'gui', f'qt{PYQT_VERSION}')



    @property
    def _stlPath(self)->str:
        ''' Returns the path where STL files are stored '''

        return os.path.join(self._pluginPath, 'stl')



    @property
    def _settingsFilePath(self)->str:
        ''' Returns the path of the settings file '''

        return os.path.join(self._pluginPath, 'settings.json')



    _cachedRemoveModelsButton = None

    @property
    def _removeAutoTowerButton(self)->QObject:
        ''' Returns the button used to remove the Auto Tower from the scene '''

        if self._cachedRemoveModelsButton is None:
            self._cachedRemoveModelsButton = self._createDialog('RemoveModelsButton.qml')
        return self._cachedRemoveModelsButton



    _cachedSettingsDialog = None

    @property
    def _settingsDialog(self)->QObject:
        ''' Returns the settings dialog '''

        if self._cachedSettingsDialog is None:
            self._cachedSettingsDialog = self._createDialog('SettingsDialog.qml')
        return self._cachedSettingsDialog



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
            self._cachedFanTowerController = FanTowerController.FanTowerController(self._guiPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedFanTowerController



    _cachedRetractionDistanceTowerController = None

    @property
    def _retractionDistanceTowerController(self)->RetractDistanceTowerController:
        ''' Returns the object used to create a Retraction Distance Tower '''

        if self._cachedRetractionDistanceTowerController is None:
            self._cachedRetractionDistanceTowerController = RetractDistanceTowerController.RetractDistanceTowerController(self._guiPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedRetractionDistanceTowerController



    _cachedRetractionSpeedTowerController = None

    @property
    def _retractionSpeedTowerController(self)->RetractSpeedTowerController:
        ''' Returns the object used to create a Retraction Speed Tower '''

        if self._cachedRetractionSpeedTowerController is None:
            self._cachedRetractionSpeedTowerController = RetractSpeedTowerController.RetractSpeedTowerController(self._guiPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedRetractionSpeedTowerController



    _cachedTempTowerController = None

    @property
    def _tempTowerController(self)->TempTowerController:
        ''' Returns the object used to create a Temperature Tower '''

        if self._cachedTempTowerController is None:
            self._cachedTempTowerController = TempTowerController.TempTowerController(self._guiPath, self._stlPath, self._loadStlCallback, self._generateAndLoadStlCallback)
        return self._cachedTempTowerController



    _settingsTable = None

    @property
    def _settings(self)->dict:
        ''' Provides lazy initialization of plugin settings '''

        if self._settingsTable == None:
            try:
                # Load settings from the settings file, if it exists
                with open(self._settingsFilePath, 'r') as settingsFile:
                    self._settingsTable = json.load(settingsFile)

                # Forward the OpenScad path to the OpenScadInterface object
                self._openScadInterface.SetOpenScadPath(self._settingsTable['openscad path'])

            except:
                # Initialize settings with default values
                self._settingsTable = {
                    'openscad path': self._openScadInterface.OpenScadPath,
                }

        return self._settingsTable



    _cachedOpenScadInterface = None
    @property
    def _openScadInterface(self)->OpenScadInterface.OpenScadInterface:
        ''' Provides lazy instantiation of the OpenScad interface '''

        if self._cachedOpenScadInterface is None:
            self._cachedOpenScadInterface = OpenScadInterface.OpenScadInterface()

        return self._cachedOpenScadInterface



    # The path to the OpenSCAD program
    openScadPathChanged = pyqtSignal()

    # Called to set the OpenSCAD path
    def setOpenScadPath(self, value)->None:
        ''' Ensures an openscad path provided by the user is properly formatted '''

        # Ensure the path ends with the openscad executable file name
        if value != '':
            if platform.system().lower() == 'windows':
                if value.lower().endswith('openscad') == False and value.lower().endswith('openscad.exe') == False:
                    value = os.path.join(value, 'openscad.exe')
            else:
                if value.lower().endswith('openscad') == False:
                    value = os.path.join(value, 'openscad')

        # Forward the OpenScad path to the OpenScadInterface object
        self._openScadInterface.SetOpenScadPath(value)

        # Notify listeners that the path has changed
        self.openScadPathChanged.emit()

    # Returns the OpenSCAD path
    @pyqtProperty(str, notify=openScadPathChanged, fset=setOpenScadPath)
    def openScadPath(self)->str:
        ''' Provides access to the openscad path for the settings dialog ''' 

        return self._openScadInterface.OpenScadPath



    autoTowerGeneratedChanged = pyqtSignal()
    @pyqtProperty(bool, notify=autoTowerGeneratedChanged)
    def autoTowerGenerated(self)->bool:
        ''' Used to show or hide the button for removing the generated Auto Tower '''

        return self._autoTowerGenerated



    @pyqtSlot()
    def removeButtonClicked(self)->None:
        ''' Called when the remove button is clicked to remove the generated Auto Tower from the scene'''

        # Remove the tower
        self._removeAutoTower()

        # Notify the user that the Auto Tower has been removed
        Message('The Auto Tower model and its associated post-processing has been removed', title=self._pluginName).show()



    @pyqtSlot()
    def saveSettings(self)->None:
        ''' Saves plugin settings to a json file so they persist between sessions '''

        # Update the OpenScad path from the OpenScadInterface object
        self._settings['openscad path'] = self._openScadInterface.OpenScadPath

        # Save the settings to the settings file
        with open(self._settingsFilePath, 'w') as settingsFile:
            json.dump(self._settings, settingsFile)



    def _executeIfOpenScadPathIsValid(self, function)->None:
        ''' Checks if the OpenScad path is valid and, if it is, executes the provided function
            This should be used to protect any function that relies on OpenSCAD '''

        # If the OpenSCAD path is valid, execute the function
        if self._openScadInterface.OpenScadPathValid:
            function()

        # If the OpenSCAD path is not valid, prompt the user to set it
        else:
            message = 'This function requires OpenSCAD ((https://openscad.org/)\n'
            message += 'Ensure it is installed and the path is set correctly in the plugin\n'
            if self._openScadInterface.OpenScadPath != '':
                message += f'The current path is {self._openScadInterface.OpenScadPath}\n'

            Message(message, title=self._pluginName).show()




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

        # Stop listening for machine and layer height changes
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

        qml_file_path = os.path.join(self._guiPath, qml_filename)
        dialog = Application.getInstance().createQmlComponent(qml_file_path, {'manager': self})
        return dialog



    def _displayRemoveAutoTowerButton(self)->None:
        ''' Adds a button to Cura's window to remove the Auto Tower '''

        CuraApplication.getInstance().addAdditionalComponent('saveButton', self._removeAutoTowerButton)



    def _loadStlCallback(self, stlFilePath, postProcessingCallback)->None:
        ''' This callback is called by the tower model controller if a preset tower is requested '''

        # If the file does not exist, display an error message
        if os.path.isfile(stlFilePath) == False:
            Logger.log('e', f'The preset file "{stlFilePath}" does not exist')
            Message(f'The selected preset is not available', title = self._pluginName).show()
            return

        # Import the STL file into the scene
        self._importStl(stlFilePath, postProcessingCallback)



    def _generateAndLoadStlCallback(self, openScadFilename, openScadParameters, postProcessingCallback)->None:
        ''' This callback is called by the tower model controller after a tower has been configured to generate an STL model from an OpenSCAD file '''

        # Record the current layer height
        self._generatedLayerHeight = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty('layer_height', 'value')
        self._currentLayerHeight = self._generatedLayerHeight

        # Record the current state of the support enabled setting
        self._currentSupportEnabled = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty('support_enable', 'value')

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
        Logger.log('d', f'Running OpenSCAD in the background')
        
        # Start the generation process
        job = OpenScadJob.OpenScadJob(self._openScadInterface, openScadFilePath, openScadParameters, stlFilePath)
        job.run()

        # Wait for OpenSCAD to finish
        # This should probably be done by having a function called when the job finishes...
        while (job.isRunning()):
            pass
        Logger.log('d', f'OpenSCAD finished')

        # Make sure the STL file was generated
        if os.path.isfile(stlFilePath) == False:
            Logger.log('e', f'Failed to generate {stlFilePath} from {openScadFilename}')
            errorMessage = self._openScadInterface.errorMessage
            Message(f'OpenSCAD Failed with message:\n{errorMessage})', title = self._pluginName).show()
            self._waitDialog.hide()
            return

        # Import the STL file into the scene
        self._importStl(stlFilePath, postProcessingCallback)



    def _importStl(self, stlFilePath, postProcessingCallback)->None:
        ''' Imports an STL file into the scene '''

        # Remove all models from the scene
        self._autoTowerGenerated = False
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

        # Display a warning if supports are enabled        
        if self._currentSupportEnabled == True:
            Message('The "Generate Support" option is selected. For best results, deselect this before printing').show()



    def _onMachineChanged(self)->None:
        ''' Listen for machine changes made after an Auto Tower is generated 
            In this case, the Auto Tower needs to be removed and regenerated '''

        self._removeAutoTower()
        Message('The Auto Tower has been removed because the active machine was changed', title=self._pluginName).show()        



    def _onPrintSettingChanged(self, setting_key, property_name)->None:
        ''' Listen for setting changes made after an Auto Tower is generated '''

        # This check is redundant and probably not needed
        if self._autoTowerGenerated == True:

            # Warn the user if the layer height changes
            if setting_key == 'layer_height' and property_name == 'value':
                layerHeight = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty('layer_height', 'value')
                if layerHeight != self._generatedLayerHeight and layerHeight != self._currentLayerHeight:
                    self._currentLayerHeight = self._generatedLayerHeight
                    Message('The layer height has changed. For best results, regenerate the Auto Tower').show()

            # Warn the user if supports are enabled
            if setting_key == 'support_enable' and property_name == 'value':
                support_enabled = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty('support_enable', 'value')
                if support_enabled == True and self._currentSupportEnabled != True:
                    Message('The "Generate Support" option has been selected. For best results, deselect this before printing').show()
                self._currentSupportEnabled = support_enabled
                



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
