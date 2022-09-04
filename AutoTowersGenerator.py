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



    def __init__(self):
        QObject.__init__(self)
        Extension.__init__(self)

        # Add menu items for this plugin
        self.setMenuName('Auto Towers')
        self.addMenuItem('Fan Tower', lambda: self._executeIfOpenScadPathIsValid(lambda: self._fanTowerController.generate()))
        self.addMenuItem('', lambda: None)
        self.addMenuItem('Retraction Tower (Distance)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._retractionDistanceTowerController.generate()))
        self.addMenuItem('Retraction Tower (Speed)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._retractionSpeedTowerController.generate()))
        self.addMenuItem(' ', lambda: None)
        self.addMenuItem('Temp Tower (ABS)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate('ABS')))
        self.addMenuItem('Temp Tower (PETG)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate('PETG')))
        self.addMenuItem('Temp Tower (PLA)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate('PLA')))
        self.addMenuItem('Temp Tower (PLA+)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate('PLA+')))
        self.addMenuItem('Temp Tower (TPU)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate('TPU')))
        self.addMenuItem('Temp Tower (Custom)', lambda: self._executeIfOpenScadPathIsValid(lambda: self._tempTowerController.generate(None)))
        self.addMenuItem('  ', lambda: None)
        self.addMenuItem('Settings', lambda: self._settingsDialog.show())

        # Create a temporary folder
        self._temporaryFolder = tempfile.TemporaryDirectory()

        # Initialize the OpenSCAD interface object
        self._openScadInterface = OpenScadInterface.OpenScadInterface()

        # Keep track of the post-processing callback and the node added by the OpenSCAD import
        self._postProcessingCallback = None
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
        CuraApplication.getInstance().mainWindowChanged.connect(self._createRemoveButton)

        # Connect our post-processing capabilities to be called when printing starts
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self._postProcess)



    _cachedPluginPath = None
    @property
    def _pluginPath(self):
        ''' Returns the path to the plugin directory '''

        if self._cachedPluginPath is None:
            self._cachedPluginPath = PluginRegistry.getInstance().getPluginPath(self.getPluginId())
        return self._cachedPluginPath



    @property
    def _stlPath(self):
        ''' Returns the path to the directory where STL models are generated '''

        return self._temporaryFolder.name



    @property
    def _openScadSourcePath(self):
        ''' Returns the path to the OpenSCAD source models'''

        return os.path.join(self._pluginPath, 'openscad')


    
    @property
    def _guiPath(self):
        ''' Returns the path to the GUI files directory '''

        return os.path.join(self._pluginPath, 'gui', f'qt{PYQT_VERSION}')



    @property
    def _settingsFilePath(self):
        ''' Returns the path of the settings file '''
        return os.path.join(self._pluginPath, 'settings.json')


    _cachedRemoveModelsButton = None
    @property
    def _removeModelsButton(self):
        ''' Returns the button used to remove the Auto Tower from the scene '''

        if self._cachedRemoveModelsButton is None:
            self._cachedRemoveModelsButton = self._createDialog('RemoveModelsButton.qml')
        return self._cachedRemoveModelsButton



    _cachedSettingsDialog = None
    @property
    def _settingsDialog(self):
        ''' Returns the settings dialog '''

        if self._cachedSettingsDialog is None:
            self._cachedSettingsDialog = self._createDialog('SettingsDialog.qml')
        return self._cachedSettingsDialog



    _cachedWaitDialog = None
    @property
    def _waitDialog(self):
        ''' Returns the dialog used to tell the user that generating a model may take a long time '''

        if self._cachedWaitDialog is None:
            self._cachedWaitDialog = self._createDialog('WaitDialog.qml')
        return self._cachedWaitDialog



    _cachedFanTowerController = None
    @property
    def _fanTowerController(self):
        ''' Returns the object used to create a Fan Tower '''

        if self._cachedFanTowerController is None:
            self._cachedFanTowerController = FanTowerController.FanTowerController(self._guiPath, self._modelCallback)
        return self._cachedFanTowerController



    _cachedRetractionDistanceTowerController = None
    @property
    def _retractionDistanceTowerController(self):
        ''' Returns the object used to create a Retraction Distance Tower '''

        if self._cachedRetractionDistanceTowerController is None:
            self._cachedRetractionDistanceTowerController = RetractDistanceTowerController.RetractDistanceTowerController(self._guiPath, self._modelCallback)
        return self._cachedRetractionDistanceTowerController



    _cachedRetractionSpeedTowerController = None
    @property
    def _retractionSpeedTowerController(self):
        ''' Returns the object used to create a Retraction Speed Tower '''

        if self._cachedRetractionSpeedTowerController is None:
            self._cachedRetractionSpeedTowerController = RetractSpeedTowerController.RetractSpeedTowerController(self._guiPath, self._modelCallback)
        return self._cachedRetractionSpeedTowerController



    _cachedTempTowerController = None
    @property
    def _tempTowerController(self):
        ''' Returns the object used to create a Temperature Tower '''

        if self._cachedTempTowerController is None:
            self._cachedTempTowerController = TempTowerController.TempTowerController(self._guiPath, self._modelCallback)
        return self._cachedTempTowerController



    _settingsTable = None
    @property
    def _settings(self):
        ''' Provides lazy initialization of plugin settings '''

        if self._settingsTable == None:
            try:
                # Load settings from the settings file, if it exists
                with open(self._settingsFilePath, 'r') as settingsFile:
                    self._settingsTable = json.load(settingsFile)
            except:
                # Initialize settings with default values
                self._settingsTable = {
                    'openscad path': '',
                }

        return self._settingsTable



    # The path to the OpenSCAD program
    openScadPathChanged = pyqtSignal()
    


    # Called to set the OpenSCAD path
    def setOpenScadPath(self, value):
        # Ensure the path ends with the openscad executable
        if value != '':
            if platform.system().lower() == 'windows':
                if value.lower().endswith('openscad') == False and value.lower().endswith('openscad.exe') == False:
                    value = os.path.join(value, 'openscad.exe')
            else:
                if value.lower().endswith('openscad') == False:
                    value = os.path.join(value, 'openscad')

        self._settings['openscad path'] = value
        self.openScadPathChanged.emit()



    # Returns the OpenSCAD path
    @pyqtProperty(str, notify=openScadPathChanged, fset=setOpenScadPath)
    def openScadPath(self) -> str:
        if self._settings['openscad path'] != '':
            return self._settings['openscad path']
        else:
            return self._openScadInterface.DefaultOpenScadPath



    autoTowerGeneratedChanged = pyqtSignal()
    @pyqtProperty(bool, notify=autoTowerGeneratedChanged)
    def autoTowerGenerated(self):
        ''' Used to show or hide the button for removing the generated Auto Tower '''

        return self._autoTowerGenerated



    @pyqtSlot()
    def removeButtonClicked(self):
        ''' Called when the remove button is clicked to remove the generated Auto Tower from the scene'''

        # Remove the tower
        self._removeAutoTower()

        # Notify the user that the Auto Tower has been removed
        Message('The Auto Tower model and its associated post-processing has been removed', title=self._pluginName).show()



    @pyqtSlot()
    def saveSettings(self):
        ''' Saves plugin settings to a json file so they persist between sessions '''

        with open(self._settingsFilePath, 'w') as settingsFile:
            json.dump(self._settings, settingsFile)



    def _executeIfOpenScadPathIsValid(self, function):
        ''' Executes the specified function if the OpenSCAD path is valid
            This should be used to protect any function that relies on OpenSCAD '''

        # If the OpenSCAD path is not valid, prompt the user to set it
        if self.openScadPath == '':
            Message('The OpenSCAD path was unable to be determined. Please configure it manually and try again.').show()
            self._settingsDialog.show()

        # If the OpenSCAD path is valid, execute the function
        else:
            function()




    def _removeAutoTower(self):
        ''' Removes the generated Auto Tower and post-processing callbacks '''

        # Indicate that there is no longer an Auto Tower in the scene
        self._autoTowerGenerated = False
        self.autoTowerGeneratedChanged.emit()

        # Remove the Auto Tower itself
        self._autoTowerOperation.undo()

        # Remove the post-processing callback
        self._postProcessingCallback = None

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


    def _createDialog(self, qml_filename):
        ''' Creates a dialog object from a QML file name 
            The QML file is assumed to be in the GUI directory             
            Returns a dialog object, with this object assigned as the "manager" '''

        qml_file_path = os.path.join(self._guiPath, qml_filename)
        dialog = Application.getInstance().createQmlComponent(qml_file_path, {'manager': self})
        return dialog



    def _createRemoveButton(self):
        ''' Adds a button to Cura's window to remove the Auto Tower '''

        CuraApplication.getInstance().addAdditionalComponent('saveButton', self._removeModelsButton)



    def _generateStlFilename(self, openScadFilename, openScadParameters):
        ''' Generates a (hopefully) unique STL filename from an OpenSCAD source file name and the parameters used to generate the STL model '''

        # Combine the OpenSCAD file name and the parameters into a single string and then generate a hash for it
        # 64 bits is a bit of overkill, so it's cut down to make a smaller file name with a larger chance of name clashes
        parameterValues = [str(value) for value in list(openScadParameters.values())]
        stringToHash = openScadFilename + ' '.join(parameterValues)
        hashedString = hashlib.sha256(stringToHash.encode()).hexdigest()
        hashedInt = int(hashedString, 16)
        halfHashedInt = hashedInt >> 128
        halfHashedString = f'{halfHashedInt:x}'
        
        # The STL filename is the hashed string with a .stl extension
        stlFilename = f'{halfHashedString}.stl'
        return stlFilename



    def _modelCallback(self, openScadFilename, openScadParameters, _postProcessingCallback):
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
        stlFilename = self._generateStlFilename(openScadFilename, openScadParameters)
        stlFilePath = os.path.join(self._stlPath, stlFilename)

        # If the needed STL file does not already exist, generate it from scratch
        if os.path.isfile(stlFilePath) == False:
            # Since it can take a while to generate the STL file, do it in a separate thread to allow the GUI to remain responsive
            Logger.log('d', f'Running OpenSCAD in the background')
            
            # Start the generation process
            job = OpenScadJob.OpenScadJob(self._openScadInterface, openScadFilePath, openScadParameters, stlFilePath, self.openScadPath)
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
        self._autoTowerOperation = MeshImporter.ImportMesh(stlFilePath, False)
        CuraApplication.getInstance().processEvents()

        # Register the post-processing callback for this particular tower
        self._postProcessingCallback = _postProcessingCallback

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



    def _onMachineChanged(self):
        ''' Listen for machine changes made after an Auto Tower is generated 
            In this case, the Auto Tower needs to be removed and regenerated '''

        self._removeAutoTower()
        Message('The Auto Tower has been removed because the active machine was changed', title=self._pluginName).show()        



    def _onPrintSettingChanged(self, setting_key, property_name):
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
                



    def _postProcess(self, output_device):
        ''' This callback is called just before gcode is generated for the model 
            (this happens when the sliced model is sent to the printer or a file '''

        # Proceed if a post-processing callback has been registered
        if not self._postProcessingCallback is None:

            # Proceed if there is g-code in the scene
            scene = Application.getInstance().getController().getScene()
            if hasattr(scene, 'gcode_dict'):

                # Proceed if the g-code is valid
                gcode_dict = getattr(scene, 'gcode_dict')
                if gcode_dict:

                    # Proceed if there is g-code for the current build plate
                    active_build_plate_id = CuraApplication.getInstance().getMultiBuildPlateModel().activeBuildPlate
                    gcode = gcode_dict[active_build_plate_id]
                    if gcode:

                        # Proceed if the g-code has not already been post-processed
                        if ';POSTPROCESSED' not in gcode[0]:

                            # Call the callback to post-process the g-code
                            gcode = self._postProcessingCallback(gcode)

                            # Mark the g-code as having been post-processed
                            gcode[0] += ';POSTPROCESSED\n'

                        else:
                            Logger.log('e', 'G-code has already been post-processed')
