import glob
import os
import platform
import traceback

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
    PYQT_VERSION = 6
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty
    PYQT_VERSION = 5

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Message import Message
from UM.PluginRegistry import PluginRegistry

from UM.i18n import i18nCatalog
from UM.Resources import Resources


from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager

from . import MeshImporter
from .PluginSettings import PluginSettings
from .OpenScadInterface import OpenScadInterface
from .OpenScadJob import OpenScadJob

from .Controllers.BedLevelPatternContoller import BedLevelPatternController
from .Controllers.FanTowerController import FanTowerController
from .Controllers.FlowTowerController import FlowTowerController
from .Controllers.RetractTowerController import RetractTowerController
from .Controllers.SpeedTowerController import SpeedTowerController
from .Controllers.TempTowerController import TempTowerController

# not sure it's necessar i18n could be store in a different place ?
Resources.addSearchPath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)),'Resources')
)  # Plugin translation file import

catalog = i18nCatalog("autotowers")

if catalog.hasTranslationLoaded():
    Logger.log("i", "Auto Towers Generator Plugin translation loaded!")

class AutoTowersGenerator(QObject, Extension):

    # Add additional controller classes to this list
    _controllerClasses = [BedLevelPatternController, FanTowerController, FlowTowerController, RetractTowerController, SpeedTowerController, TempTowerController]



    def __init__(self):
        QObject.__init__(self)
        Extension.__init__(self)

        self._pluginSettings = None

        # Keep track of the post-processing callback and the node added by the OpenSCAD import
        self._towerControllerPostProcessingCallback = None
        self._importedNode = None

        # Keep track of whether a model has been generated and is in the scene
        self._autoTowerNode = None
        self._autoTowerOperation = None

        # Keep track of the currently active tower controller
        self._currentTowerController = None

        # Update the view when the main window is changed so the "remove" button is always visible when enabled
        CuraApplication.getInstance().mainWindowChanged.connect(self._displayRemoveAutoTowerButton)

        # Finish initializing the plugin after Cura is fully ready
        CuraApplication.getInstance().pluginsLoaded.connect(self._onPluginsLoadedCallback)

        # Make sure the tower is cleaned up before the application closes
        CuraApplication.getInstance().getOnExitCallbackManager().addCallback(self._onExitCallback)



    @property
    def _pluginDir(self)->str:
        ''' Returns the path to the plugin directory '''

        return PluginRegistry.getInstance().getPluginPath(self.getPluginId())



    @property
    def _openScadSourcePath(self)->str:
        ''' Returns the path to the OpenSCAD source models'''

        return os.path.join(self._pluginDir, 'Resources', 'OpenScad')


    
    @property
    def _qmlDir(self)->str:
        ''' Returns the location of the QML dialog files directory '''

        return os.path.join(self._pluginDir, 'Resources', 'QML', f'QT{PYQT_VERSION}')



    @property
    def _stlDir(self)->str:
        ''' Returns the directory where STL files are stored '''

        return os.path.join(self._pluginDir, 'Resources', 'STL')



    @property
    def _tempDir(self)->str:
        ''' Returns the directory to use for temporary files '''

        return os.path.join(self._pluginDir, 'tmp')



    @property
    def _pluginSettingsFilePath(self)->str:
        ''' Returns the path to the plugin settings file '''

        return os.path.join(self._pluginDir, 'pluginSettings.json')



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



    _cachedSettingsVerificationDialog = None

    @property
    def _settingsVerificationDialog(self)->QObject:
        ''' Returns a dialog asking the user whether they want to continue with incompatible settings '''

        if self._cachedSettingsVerificationDialog is None:
            self._cachedSettingsVerificationDialog = self._createDialog('SettingsVerificationDialog.qml')
        return self._cachedSettingsVerificationDialog




    _cachedWaitDialog = None

    @property
    def _waitDialog(self)->QObject:
        ''' Returns the dialog used to tell the user that generating a model may take a long time '''

        if self._cachedWaitDialog is None:
            self._cachedWaitDialog = self._createDialog('WaitDialog.qml')
        return self._cachedWaitDialog



    _cachedOpenScadInterface = None
    @property
    def _openScadInterface(self)->OpenScadInterface:
        ''' Provides lazy instantiation of the OpenScad interface '''

        if self._cachedOpenScadInterface is None:
            self._cachedOpenScadInterface = OpenScadInterface(self._pluginName, self._tempDir)

        return self._cachedOpenScadInterface



    @pyqtProperty(str)
    def os(self)->str:
        ''' Return the operating system being used '''

        return platform.system().lower()


    autoTowerGeneratedChanged = pyqtSignal()
    @pyqtProperty(bool, notify=autoTowerGeneratedChanged)
    def autoTowerGenerated(self)->bool:
        ''' Used to show or hide the button for removing the generated Auto Tower '''

        return not self._autoTowerOperation is None



    @property
    def _pluginName(self)->str:
        ''' Returns the plugin's name '''

        return self.getPluginId()
    


    @pyqtProperty(str)
    def pluginVersion(self)->str:
        ''' Returns the plugin's version number '''

        return self.getVersion()



    _openScadPathSettingChanged = pyqtSignal()
    
    def setOpenScadPathSetting(self, value)->None:
        self._pluginSettings.SetValue('openscad path', value)
        self._openScadInterface.SetOpenScadPath(value)

        # Warn the user if the OpenScad path is not valid
        if not self._openScadInterface.OpenScadPathValid:
            message = f'{catalog.i18nc("@msg", "The OpenScad path")} "{self._openScadInterface.OpenScadPath}" {catalog.i18nc("@msg", "is not valid")}'
            Message(message, title=self._pluginName, message_type=Message.MessageType.ERROR).show()

        # Notify the user of the detected OpenScad version number and path
        else:
            message = f'{catalog.i18nc("@msg", "Found OpenScad version")} {self._openScadInterface.OpenScadVersion} {catalog.i18nc("@msg", "at")} {self._openScadInterface.OpenScadPath}'
            Message(message, title=self._pluginName, message_type=Message.MessageType.POSITIVE, lifetime=5).show()

        self._openScadPathSettingChanged.emit()

    @pyqtProperty(str, notify=_openScadPathSettingChanged, fset=setOpenScadPathSetting)
    def openScadPathSetting(self)->str:
        # If the OpenSCAD path has not been set, use the default from the OpenSCAD interface
        value = self._pluginSettings.GetValue('openscad path')
        if value == '':
            # Update the OpenScad path from the OpenScad interface
            value = self._openScadInterface.OpenScadPath

        return value



    _correctPrintSettings = True

    _correctPrintSettingsChanged = pyqtSignal()

    def setCorrectPrintSettings(self, value:bool)->None:
        self._pluginSettings.SetValue('correct print settings', value)
        self._correctPrintSettingsChanged.emit()

    @pyqtProperty(bool, notify=_correctPrintSettingsChanged, fset=setCorrectPrintSettings)
    def correctPrintSettings(self)->bool:
        return self._pluginSettings.GetValue('correct print settings', True)



    _enableLcdMessagesSetting = True

    _enableLcdMessagesSettingChanged = pyqtSignal()

    def setEnableLcdMessagesSetting(self, value:bool)->None:
        self._pluginSettings.SetValue('enable lcd messages', value)
        self._enableLcdMessagesSettingChanged.emit()

    @pyqtProperty(bool, notify=_enableLcdMessagesSettingChanged, fset=setEnableLcdMessagesSetting)
    def enableLcdMessagesSetting(self)->bool:
        return self._pluginSettings.GetValue('enable lcd messages', False)


    _enableAdvancedGcodeCommentsSetting = True

    _enableAdvancedGcodeCommentsSettingChanged = pyqtSignal()

    def setAdvancedGcodeCommentsSetting(self, value:bool)->None:
        self._pluginSettings.SetValue('advanced gcode comments', value)
        self._enableAdvancedGcodeCommentsSettingChanged.emit()

    @pyqtProperty(bool, notify=_enableAdvancedGcodeCommentsSettingChanged, fset=setAdvancedGcodeCommentsSetting)
    def enableAdvancedGcodeCommentsSetting(self)->bool:
        return self._pluginSettings.GetValue('advanced gcode comments', True)

    @pyqtSlot()
    def removeButtonClicked(self)->None:
        ''' Called when the remove button is clicked to remove the generated Auto Tower from the scene'''

        # Remove the tower
        self._removeAutoTower()



    _cachedControllerTable = {}
    def _retrieveTowerController(self, ControllerClass):
        ''' Provides lazy instantiation of the tower controllers '''
    
        if not ControllerClass in self._cachedControllerTable:
            self._cachedControllerTable[ControllerClass] = ControllerClass(guiDir=self._qmlDir, stlDir=self._stlDir, loadStlCallback=self._loadStlCallback, generateStlCallback=self._generateStlCallback, pluginName=self._pluginName)
        return self._cachedControllerTable[ControllerClass]



    def _initializeMenu(self)->None:
        # Add a menu for this plugin
        self.setMenuName(catalog.i18nc("@menu", "Auto Towers"))

        # Add menu entries for each tower controller
        for controllerClass in self._controllerClasses:
            controller = self._retrieveTowerController(controllerClass)
            self.addMenuItem(controller.name, lambda controllerClass=controllerClass: self._generateAutoTower(controllerClass))

        # Add a menu item for modifying plugin settings
        self.addMenuItem(' ', lambda: None)
        self.addMenuItem(catalog.i18nc("@menu", "Settings"), lambda: self._displayPluginSettingsDialog())



    def _generateAutoTower(self, controllerClass):
        ''' Tell the current tower controller to generate a tower '''

        # Generate the auto tower
        currentTowerController = self._retrieveTowerController(controllerClass)
        currentTowerController.generate(customizable=self._openScadInterface.OpenScadPathValid)



    def _removeAutoTower(self, message = None)->None:
        ''' Removes the generated Auto Tower and post-processing callbacks '''
        
        # Stop listening for callbacks
        self._towerControllerPostProcessingCallback = None
        Application.getInstance().getOutputDeviceManager().writeStarted.disconnect(self._postProcessCallback)
        # BAK: 25 Nov 2022 - Removing these callbacks for now, because they're catching changes they shouldn't and removing towers inappropriately
        # CuraApplication.getInstance().getMachineManager().activeMachine.propertyChanged.disconnect(self._onPrintSettingChanged)
        # ExtruderManager.getInstance().getActiveExtruderStack().propertiesChanged.disconnect(self._onExtruderPrintSettingChanged)
        CuraApplication.getInstance().getController().getScene().getRoot().childrenChanged.disconnect(self._onSceneChanged)
        try:
            CuraApplication.getInstance().getMachineManager().globalContainerChanged.disconnect(self._onMachineChanged)
        except TypeError as e:
            # This exception is expected during Cura shutdown
            pass

        # Remove the Auto Tower itself
        if not self._autoTowerOperation is None:
            self._autoTowerOperation.undo()
            self._autoTowerOperation = None
            CuraApplication.getInstance().deleteAll()

        # Clear the job name
        CuraApplication.getInstance().getPrintInformation().setJobName('')

        # Indicate that there is no longer an Auto Tower in the scene
        self.autoTowerGeneratedChanged.emit()

        # Clean up after the AutoTower
        if not self._currentTowerController is None:
            restoredSettings = self._currentTowerController.cleanup()
            if len(restoredSettings) > 0:
                message = message + '\n' if not message is None else ''
                message += catalog.i18nc("@msg", "The following settings were restored :\n")
                message += '\n'.join([f'{catalog.i18nc("@msg", "Restored")} {entry[0]} {catalog.i18nc("@msg", "to")} {entry[1]}' for entry in restoredSettings])
            if message is not None: 
                Message(message, title=self._pluginName, lifetime=5).show()
            self._currentTowerController = None

        CuraApplication.getInstance().processEvents()



    def _createDialog(self, qml_filename)->QObject:
        ''' Creates a dialog object from a QML file name 
            The QML file is assumed to be in the GUI directory             
            Returns a dialog object, with this object assigned as the "manager" '''

        qml_file_path = os.path.join(self._qmlDir, qml_filename)
        dialog = Application.getInstance().createQmlComponent(qml_file_path, {'manager': self})
        return dialog



    def _displayRemoveAutoTowerButton(self)->None:
        ''' Adds a button to Cura's window to remove the Auto Tower '''

        CuraApplication.getInstance().addAdditionalComponent('saveButton', self._removeAutoTowerButton)



    def _displayPluginSettingsDialog(self)->None:
        ''' Prepares and displays the plugin settings dialog '''

        self._pluginSettingsDialog.show()



    def _loadStlCallback(self, controller, towerName, stlFilePath, postProcessingCallback)->None:
        ''' This callback is called by the tower model controller if a preset tower is requested '''

        # If the file does not exist, display an error message
        if os.path.isfile(stlFilePath) == False:
            errorMessage = f'{catalog.i18nc("@msg", "The STL file")} "{stlFilePath}" {catalog.i18nc("@msg", "does not exist")}'
            Logger.log('e', errorMessage)
            Message(errorMessage, title = self._pluginName, message_type=Message.MessageType.ERROR).show()
            return

        # Import the STL file into the scene
        self._importStl(controller, towerName, stlFilePath, postProcessingCallback)



    def _generateStlCallback(self, controller, towerName, openScadFilename, openScadParameters, postProcessingCallback)->None:
        ''' This callback is called by the tower model controller after a tower has been configured to generate an STL model from an OpenSCAD file '''

        # This could take up to a couple of minutes...
        self._waitDialog.show()
        CuraApplication.getInstance().processEvents() # Allow Cura to update itself periodically through this method
        
        # Compile the STL file name
        openScadFilePath = os.path.join(self._openScadSourcePath, openScadFilename)
        stlFilename = 'custom_autotower.stl'
        stlFilePath = os.path.join(self._tempDir, stlFilename)

        # Generate the STL file
        # Since it can take a while to generate the STL file, this is done in a separate thread to allow the GUI to remain responsive
        job = OpenScadJob(self._openScadInterface, openScadFilePath, openScadParameters, stlFilePath)
        job.run()

        # Wait for OpenSCAD to finish
        # This should probably be done by having a function called when the job finishes...
        while (job.isRunning()):
            pass

        # Make sure the STL file was generated
        if os.path.isfile(stlFilePath) == False:
            errorMessage = f'{catalog.i18nc("@msg", "Failed to generate")} "{stlFilePath}" {catalog.i18nc("@msg", "from")} "{openScadFilename}"\n{catalog.i18nc("@msg", "Command output was")}\n"{self._openScadInterface.commandResult}"'
            Message(errorMessage, title = self._pluginName, message_type=Message.MessageType.ERROR).show()
            Logger.log('e', errorMessage)
            self._waitDialog.hide()
            return

        # Import the STL file into the scene
        self._importStl(controller, towerName, stlFilePath, postProcessingCallback)



    def _importStl(self, controller, towerName, stlFilePath, postProcessingCallback)->None:
        ''' Imports an STL file into the scene '''

        # Make sure any previous auto towers are removed
        self._removeAutoTower()

        # Allow the tower controller to update Cura's settings to ensure it can be generated correctly
        recommendedSettings = controller.checkPrintSettings(self.correctPrintSettings)
        if len(recommendedSettings) > 0:
            message = '\n'.join([f'{catalog.i18nc("@msg", "Changed")} {entry[0]} {catalog.i18nc("@msg", "from")} {entry[1]} {catalog.i18nc("@msg", "to")} {entry[2]}' for entry in recommendedSettings])        
            if self.correctPrintSettings:
                message = catalog.i18nc("@msg", "The following settings were changed :\n") + message
                Message(message, title=self._pluginName, lifetime=5).show()
            else:
                message = catalog.i18nc("@msg", "The following setting changes are recommended :\n") + message
                Message(message, title=self._pluginName, message_type=Message.MessageType.WARNING, lifetime=5).show()

        # Record the new tower controller
        self._currentTowerController = controller

        # Import the STL file into the scene
        self._autoTowerOperation = MeshImporter.ImportMesh(stlFilePath, name=self._pluginName)
        CuraApplication.getInstance().processEvents()

        # The dialog is no longer needed
        self._waitDialog.hide()

        # Rename the print job
        CuraApplication.getInstance().getPrintInformation().setJobName(towerName)

        # Register that the Auto Tower has been generated
        self.autoTowerGeneratedChanged.emit()

        # Register the post-processing callback for this particular tower
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self._postProcessCallback)
        self._towerControllerPostProcessingCallback = postProcessingCallback

        # Remove the model if the machine is changed
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._onMachineChanged)

        # BAK: 25 Nov 2022 - Removing the following callbacks for now, because they're catching changes they shouldn't and removing towers inappropriately

        # # Remove the tower and post-processing if critical print settings (settings that are important for the AutoTower) are changed
        # CuraApplication.getInstance().getMachineManager().activeMachine.propertyChanged.connect(self._onPrintSettingChanged)

        # # Remove the tower and post-processing if critical print settings (settings that are important for the AutoTower) are changed
        # ExtruderManager.getInstance().getActiveExtruderStack().propertiesChanged.connect(self._onExtruderPrintSettingChanged)

        # Remove the tower and post-processing if the model is deleted or another model is added to the scene
        CuraApplication.getInstance().getController().getScene().getRoot().childrenChanged.connect(self._onSceneChanged)



    def _onMachineChanged(self)->None:
        ''' Listen for machine changes made after an Auto Tower is generated 
            In this case, the Auto Tower needs to be removed and regenerated '''           
        self._removeAutoTower(catalog.i18nc("@msg", "The Auto Tower was removed because the active machine was changed"))



    def _onPrintSettingChanged(self, settingKey, propertyName)->None:
        ''' Listen for setting changes made after an Auto Tower is generated '''

        # Remove the tower in response to changes to critical print settings
        if not self._currentTowerController is None:
            if self._currentTowerController.settingIsCritical(settingKey):
                settingLabel = CuraApplication.getInstance().getMachineManager().activeMachine.getProperty(settingKey, 'label')
                self._removeAutoTower(f'{catalog.i18nc("@msg", "The Auto Tower was removed because the Cura setting")} "{settingLabel}" {catalog.i18nc("@msg", "has changed since the tower was generated")}')



    def _onActiveExtruderChanged(self)->None:
        ''' Listen for changes to the active extruder '''
            
        self._removeAutoTower(catalog.i18nc("@msg", "The Auto Tower was removed because the active extruder changed"))



    def _onExtruderPrintSettingChanged(self, settingKey, propertyName)->None:
        ''' Listen for changes to the active extruder print settings '''

        # Remove the tower in response to changes to critical print settings
        if not self._currentTowerController is None:
            if self._currentTowerController.settingIsCritical(settingKey):
                settingLabel = ExtruderManager.getInstance().getActiveExtruderStack().getProperty(settingKey, 'label')
                self._removeAutoTower(f'The Auto Tower was removed because the Cura setting "{settingLabel}" has changed since the tower was generated')



    def _onPluginsLoadedCallback(self)->None:
        ''' Called after plugins have been loaded
            Iniializing here means that Cura is fully ready '''

        self._pluginSettings = PluginSettings(self._pluginSettingsFilePath)
        # Init openscad path
        self._openScadInterface.SetOpenScadPath(self._pluginSettings.GetValue('openscad path'))        
        
        self._initializeMenu()



    def _onSceneChanged(self, node)->None:
        # Only process root node change
        if node.getName() == 'Root':
            # If the AutoTower node no longer exists, then clean up
            AutoTowerNodes = [child for child in node.getChildren() if child.getName() == self._pluginName]
            if len(AutoTowerNodes) <= 0:
                self._removeAutoTower()



    def _onExitCallback(self)->None:
        ''' Called as Cura is closing to ensure that any settings that were changed are restored before exiting '''

        # Remove the tower
        self._removeAutoTower(catalog.i18nc("@msg", "Removing the autotower because Cura is closing"))

        # Save the plugin settings
        try:
            self._pluginSettings.SaveToFile(self._pluginSettingsFilePath)
        except AttributeError:
            pass

        # Clear the temp directory
        for file in glob.glob(os.path.join(self._tempDir, '*')):
            os.remove(file)

        CuraApplication.getInstance().triggerNextExitCheck()        



    def _postProcessCallback(self, output_device)->None:
        ''' This callback is called just before gcode is generated for the model 
            (this happens when the sliced model is sent to the printer or a file '''
        
        # Retrieve the g-code
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
        except (TypeError, KeyError):
            # If there is no g-code for the current build plate, there's nothing more to do
            return

        try:
            gcodeProcessedMarker = f';{self._pluginName}: Post-processed by {self._pluginName} version {self.pluginVersion}'

            # Proceed if the g-code has not already been post-processed
            if gcodeProcessedMarker not in gcode[0]:

                # Mark the g-code as having been post-processed
                gcode[0] += gcodeProcessedMarker + '\n'

                # Call the tower controller post-processing callback to modify the g-code
                try:
                    gcode = self._towerControllerPostProcessingCallback(gcode, self.enableLcdMessagesSetting, self.enableAdvancedGcodeCommentsSetting)
                except Exception as e:
                    message = f'{catalog.i18nc("@msg", "An exception occured during post-processing")} : {e}'
                    Message(f'{message}', title=self._pluginName, message_type=Message.MessageType.ERROR).show()
                    Logger.log('e', f'{message}\n{traceback.format_exc()}')

        except IndexError:
            # This will be thrown if there is no gcode available
            pass
        