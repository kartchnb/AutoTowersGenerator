import glob
import os
import threading
import pathlib

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, pyqtProperty

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
from . import RetractTowerController
from . import TempTowerController



class AutoTowersGenerator(QObject, Extension):
    _pluginName = 'AutoTowersGenerator'
    _preferencePathPrefix = 'autotowersgenerator'
    _openScadPathPreferencePath = f'{_preferencePathPrefix}/openscadpath'
    _stlCacheLimitPreferencePath = f'{_preferencePathPrefix}/stlCacheLimit'

    def __init__(self):
        QObject.__init__(self)
        Extension.__init__(self)

        self._preferences = CuraApplication.getInstance().getPreferences()
        self._preferences.addPreference(self._openScadPathPreferencePath, '')
        self._preferences.addPreference(self._stlCacheLimitPreferencePath, 10)

        # Add menu items for this plugin
        self.setMenuName('Auto Towers')
        self.addMenuItem('Fan Tower', lambda: self._fanTowerController.generate())
        self.addMenuItem('', lambda: None)
        self.addMenuItem('Retraction Tower (Distance)', lambda: self._retractionTowerController.generate('distance'))
        self.addMenuItem('Retraction Tower (Speed)', lambda: self._retractionTowerController.generate('speed'))
        self.addMenuItem(' ', lambda: None)
        self.addMenuItem('Temp Tower (ABS)', lambda: self._tempTowerController.generate('ABS'))
        self.addMenuItem('Temp Tower (PETG)', lambda: self._tempTowerController.generate('PETG'))
        self.addMenuItem('Temp Tower (PLA)', lambda: self._tempTowerController.generate('PLA'))
        self.addMenuItem('Temp Tower (PLA+)', lambda: self._tempTowerController.generate('PLA+'))
        self.addMenuItem('Temp Tower (TPU)', lambda: self._tempTowerController.generate('TPU'))
        self.addMenuItem('Temp Tower (Custom)', lambda: self._tempTowerController.generate(None))
        self.addMenuItem('   ', lambda: None)
        self.addMenuItem('Settings', self._displaySettingsDialog)

        # Keep track of the post-processing callback and the node added by the OpenSCAD import
        self._postProcessingCallback = None
        self._importedNode = None

        # Keep track of whether a model has been generated and is in the scene
        self._autoTowerGenerated = False
        self._autoTowerOperation = None

        # Determine the command to run OpenSCAD
        self._openScadInterface = OpenScadInterface.OpenScadInterface()
        storedOpenScadPath = self._preferences.getValue(self._openScadPathPreferencePath)
        if storedOpenScadPath:
            self._openScadInterface.OpenScadPath = storedOpenScadPath

        # Update the view when the main window is changed so the "remove" button is always visible when enabled
        # Not sure if this is needed
        CuraApplication.getInstance().mainWindowChanged.connect(self._createRemoveButton)

        # Connect our post-processing capabilities to be called when printing starts
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self._postProcess)



    autoTowerGeneratedChanged = pyqtSignal()
    @pyqtProperty(bool, notify=autoTowerGeneratedChanged)
    def autoTowerGenerated(self):
        ''' Used to show or hide the button for removing the generated Auto Tower '''
        return self._autoTowerGenerated



    @pyqtSlot()
    def removeButtonClicked(self):
        ''' Called when the remove button is clicked to remove the generated Auto Tower from the scene'''

        self._removeAutoTower()

        # Notify the user that the Auto Tower has been removed
        Message('The Auto Tower model and post-processing script have been removed', title=self._pluginName).show()



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
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.disconnect(self._onMachineChanged)
        CuraApplication.getInstance().getMachineManager().activeMachine.propertyChanged.disconnect(self._onSettingChanged)



    _cachedPluginPath = None
    @property
    def _pluginPath(self):
        ''' Returns the path to the plugin directory '''
        if self._cachedPluginPath is None:
            self._cachedPluginPath = PluginRegistry.getInstance().getPluginPath(self.getPluginId())
        return self._cachedPluginPath



    @property
    def _stlPath(self):
        ''' Returns the path to the directory use to store cached STL models '''
        return os.path.join(self._pluginPath, 'stl')



    @property
    def _openScadPath(self):
        ''' Returns the path to the OpenSCAD source models'''
        return os.path.join(self._pluginPath, 'openscad')


    
    @property
    def _guiPath(self):
        ''' Returns the path to the GUI files directory '''
        return os.path.join(self._pluginPath, 'gui')


    def _createDialog(self, qml_filename):
        ''' Creates a dialog object from a QML file name 
            The QML file is assumed to be in the GUI directory 
            
            Returns a dialog object, with this object assigned as the "manager" '''
        qml_file_path = os.path.join(self._guiPath, qml_filename)
        dialog = Application.getInstance().createQmlComponent(qml_file_path, {'manager': self})
        return dialog


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
        ''' Returns the dialog used to tell the user that generating a model may take a LOOOOONG time '''
        if self._cachedWaitDialog is None:
            self._cachedWaitDialog = self._createDialog('WaitDialog.qml')
        return self._cachedWaitDialog



    _cachedFanTowerController = None
    @property
    def _fanTowerController(self):
        ''' Returns the object used to create a Fan Tower '''
        if self._cachedFanTowerController is None:
            self._cachedFanTowerController = FanTowerController.FanTowerController(self._pluginPath, self._modelCallback)
        return self._cachedFanTowerController



    _cachedRetractionTowerController = None
    @property
    def _retractionTowerController(self):
        ''' Returns the object used to create a Retraction Tower (both speed and distance) '''
        if self._cachedRetractionTowerController is None:
            self._cachedRetractionTowerController = RetractTowerController.RetractTowerController(self._pluginPath, self._modelCallback)
        return self._cachedRetractionTowerController



    _cachedTempTowerController = None
    @property
    def _tempTowerController(self):
        ''' Returns the object used to create a Temperature Tower '''
        if self._cachedTempTowerController is None:
            self._cachedTempTowerController = TempTowerController.TempTowerController(self._pluginPath, self._modelCallback)
        return self._cachedTempTowerController



    def _createRemoveButton(self):
        ''' Adds a button to Cura's window to remove the Auto Tower '''
        CuraApplication.getInstance().addAdditionalComponent('saveButton', self._removeModelsButton)



    def _generateStlFilename(self, openScadFilename, openScadParameters):
        ''' Generates a unique STL filename from an OpenSCAD source file name and the parameters used to generate the STL model '''

        # Start by stripping the ".scad" extension from the OpenSCAD filename
        stlFilename = openScadFilename.replace('.scad', '')

        # Append each parameter and its value to the file name
        for parameter in openScadParameters:
            # Retrieve the parameter value
            value = openScadParameters[parameter]

            # Limit the parameter name to just the first 3 characters
            parameter = parameter[:3]

            # Add the parameter and value to the filename
            if isinstance(value, float):
                stlFilename += f'_{parameter}_{value:.3f}'
            else:
                stlFilename += f'_{parameter}_{value}'

        # Finally, add a ".stl" extension
        stlFilename += '.stl'

        return stlFilename



    def _modelCallback(self, openScadFilename, openScadParameters, _postProcessingCallback):
        ''' This callback is called by the tower model controller after a tower has been configured to generate an STL model from an OpenSCAD file '''

        # This could take up to a couple of minutes...
        self._waitDialog.show()
        CuraApplication.getInstance().processEvents() # Allow Cura to update itself periodically through this method

        # Remove all models from the scene
        self._autoTowerGenerated = False
        CuraApplication.getInstance().deleteAll()
        CuraApplication.getInstance().processEvents()
        
        # Compile the STL file name
        openScadFilePath = os.path.join(self._openScadPath, openScadFilename)
        stlFilename = self._generateStlFilename(openScadFilename, openScadParameters)
        stlFilePath = os.path.join(self._stlPath, stlFilename)

        # Since generating an STL from OpenSCAD can take quite a while, the generated STL files are cached
        # If the needed STL file does not exist in the cache, generate it
        if os.path.isfile(stlFilePath) == False:
            # Since it can take a while to generate the STL file, do it in a separate thread and allow the GUI to remain responsive
            Logger.log('d', f'Running OpenSCAD in the background')
            job = OpenScadJob.OpenScadJob(self._openScadInterface, openScadFilePath, openScadParameters, stlFilePath)
            job.run()
            while (job.isRunning()):
                CuraApplication.getInstance().processEvents()
            Logger.log('d', f'OpenSCAD finished')

            # Make sure the STL file was generated
            if os.path.isfile(stlFilePath) == False:
                Logger.log('e', f'Failed to generate {stlFilePath} from {openScadFilename}')
                Message(f'Failed to run OpenSCAD - Make sure the OpenSCAD path is set correctly\nPath is "{self._openScadInterface.OpenScadPath}"', title = self._pluginName).show()
                self._waitDialog.hide()
                return

            # While we're here, keep the STL cache at the requested size
            self._cullCachedStls()

        # If the a cached STL file for this tower exists, move it to the top of the cache by updating its time stamp
        else:
            pathlib.Path(stlFilePath).touch(exist_ok=True)

        # Import the STL file into the scene
        self._autoTowerOperation = MeshImporter.ImportMesh(stlFilePath, False)
        CuraApplication.getInstance().processEvents()

        # Register the post-processing callback for this particular tower
        self._postProcessingCallback = _postProcessingCallback

        # Register that the Auto Tower has been generated
        self._autoTowerGenerated = True
        self.autoTowerGeneratedChanged.emit()

        # Listen for machine and layer height changes
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._onMachineChanged)
        CuraApplication.getInstance().getMachineManager().activeMachine.propertyChanged.connect(self._onSettingChanged)

        # No more need to wait!
        self._waitDialog.hide()



    def _onMachineChanged(self):
        ''' Listen for machine changes made after an Auto Tower is generated 
            In this case, the Auto Tower needs to be removed and regenerated '''
        self._removeAutoTower()
        Message('The Auto Tower has been removed because the active machine was changed', title=self._pluginName).show()        



    def _onSettingChanged(self, setting_key, property_name):
        ''' Listen for setting changes made after an Auto Tower is generated 
            if the layer height value is changed, the Auto Tower needs to be 
            removed and regenerated '''
        if setting_key == 'layer_height' and property_name == 'value' and self._autoTowerGenerated == True:
            self._removeAutoTower()
            Message('The Auto Tower has been removed because the layer height was changed', title=self._pluginName).show()



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



    def _displaySettingsDialog(self):
        ''' Display the settings dialog '''
        self._settingsDialog.setProperty('openScadPath', self._openScadInterface.OpenScadPath)
        self._settingsDialog.setProperty('stlCacheLimit', self._preferences.getValue(self._stlCacheLimitPreferencePath))
        self._settingsDialog.show()



    @pyqtSlot()
    def settingsDialogAccepted(self):
        ''' This callback is called when the settings dialog is accepted so that the OpenSCAD command gets updated
            I know there should be a better way of doing this but I don't really have a handle on Qt yet '''
        self._openScadInterface.OpenScadPath = self._settingsDialog.property('openScadPath')
        self._preferences.setValue(self._openScadPathPreferencePath, self._openScadInterface.OpenScadPath)
        self._preferences.setValue(self._stlCacheLimitPreferencePath, self._settingsDialog.property('stlCacheLimit'))



    @pyqtSlot()
    def clearCachedStls(self):
        ''' Delete the cached STL models '''
        # Iterate over each STL file in the STL cache directory
        stlFiles = glob.glob(os.path.join(self._stlPath, '*.stl'))
        for stlFile in stlFiles:
            # Delete this STL file
            os.remove(stlFile)

        Message('All cached STL models have been deleted', title=self._pluginName).show()



    def _cullCachedStls(self):
        stlCacheLimit = int(self._preferences.getValue(self._stlCacheLimitPreferencePath))
        stlFiles = glob.glob(os.path.join(self._stlPath, '*.stl'))
        while len(stlFiles) > stlCacheLimit:
            oldestStl = min(stlFiles, key=os.path.getctime)
            Logger.log('d', f'Culling oldest cached STL "{oldestStl}"')
            os.remove(oldestStl)
            stlFiles.remove(oldestStl)