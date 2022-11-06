import os

# Import the correct version of PyQt
try:
    from PyQt6.QtCore import QObject
except ImportError:
    from PyQt5.QtCore import QObject


from cura.CuraApplication import CuraApplication

from UM.Application import Application
from UM.Logger import Logger



class ControllerBase(QObject):

    def __init__(self, name, guiPath, stlPath, loadStlCallback, generateAndLoadStlCallback, openScadFilename, qmlFilename, presetsTable, criticalPropertiesTable):
        super().__init__()
        
        self.name = name

        self._guiPath = guiPath
        self._stlPath = stlPath

        self._loadStlCallback = loadStlCallback
        self._generateAndLoadStlCallback = generateAndLoadStlCallback

        self._openScadFilename = openScadFilename
        self._qmlFilename = qmlFilename
        self._presetsTable = presetsTable
        self._criticalPropertiesTable = criticalPropertiesTable

        self._originalSettings = {}



    def getPresetNames(self)->list:
        return list(self._presetsTable.keys())



    _cachedDialog = None

    @property
    def _dialog(self)->QObject:
        ''' Lazy instantiation of this controller's dialog '''
        if self._cachedDialog is None:
            qmlFilePath = os.path.join(self._guiPath, self._qmlFilename)
            self._cachedDialog = CuraApplication.getInstance().createQmlComponent(qmlFilePath, {'manager': self})

        return self._cachedDialog



    @property
    def getCriticalProperties(self)->list:
        ''' Return the Cura properties that are critical to this tower '''
        return self._criticalPropertiesTable.keys()



    def correctPrintProperties(self)->None:
        ''' Correct property settings that are incompatible with this controller '''

        globalContainerStack = Application.getInstance().getGlobalContainerStack()
        message = ''

        # Iterate over each setting in the critical settings table
        for property_name in self._criticalPropertiesTable.keys():
            compatible_value = self._criticalPropertiesTable[property_name]
            if not compatible_value is None:
                property_options = globalContainerStack.getProperty(property_name, 'options')
                try:
                    compatible_value_name = property_options[compatible_value]
                except KeyError:
                    compatible_value_name = str(compatible_value)

                # Get the current value of the setting
                property_label = globalContainerStack.getProperty(property_name, 'label')
                original_value = globalContainerStack.getProperty(property_name, 'value')
                property_options = globalContainerStack.getProperty(property_name, 'options')

                # If the property setting needs to be corrected, backup and modify the setting
                if original_value != compatible_value:
                    self._originalSettings[property_name] = original_value
                    globalContainerStack.setProperty(property_name, 'value', compatible_value)
                    message += f'"{property_label}" was set to "{compatible_value_name}"\n'
                    Logger.log('d', f'Corrected value of "{property_label}" from "{original_value}" to "{compatible_value}"')

        if message != '':
            message = 'The following printing properties were changed for this Auto Tower:\n' + message
            message += 'The original values will be restored when the Tower is removed'

        return message



    def generate(self, preset='')->None:
        ''' Generate a tower - either a preset tower or a custom tower '''
        # If a preset was requested, load it
        if not preset == '':
            self._loadPreset(preset)
        
        # Generate a custom tower
        else:
            self._dialog.show()



    def cleanupController(self)->None:
        ''' Called when the Auto Tower is removed from the scene'''

        globalContainerStack = Application.getInstance().getGlobalContainerStack()
        if not globalContainerStack is None:
            message = ''

            # Iterate over each backed up property
            for property_name in self._originalSettings.keys():
                # Get the old value
                original_value = self._originalSettings[property_name]
                property_options = globalContainerStack.getProperty(property_name, 'options')
                try:
                    original_value_name = property_options[original_value]
                except KeyError:
                    original_value_name = str(original_value)

                # Get the label of the property
                property_label = globalContainerStack.getProperty(property_name, 'label')

                # Restore the original settings
                globalContainerStack.setProperty(property_name, 'value', original_value)
                message = f'"{property_label}" was restored to "{original_value_name}"'
                Logger.log('d', f'Restored the original value of "{property_name}" "{original_value}"')

            if message != '':
                message = 'The following print properties were restored:\n' + message

        self._originalSettings = {}

        return message

