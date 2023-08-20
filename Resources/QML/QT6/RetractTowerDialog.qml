import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: 'Retraction Tower'

    buttonSpacing: UM.Theme.getSize('default_margin').width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize('default_margin').height) + UM.Theme.getSize('button').height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor('main_background')

    // Define the width of the number input text boxes
    property int numberInputWidth: UM.Theme.getSize('button').width

    // Only display customizable options when a prest is not selected
    property bool show_custom_options: dataModel.presetName == 'Custom'



    RowLayout
    {
        id: contents
        width: dialog.width - 2 * UM.Theme.getSize('default_margin').width
        spacing: UM.Theme.getSize('default_margin').width

        // Display the icon for this tower
        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.preferredHeight: icon.height
            Layout.fillHeight: true
            color: UM.Theme.getColor('primary_button')

            Image
            {
                id: icon
                source: Qt.resolvedUrl('../../Images/retracttower_icon.png')
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        GridLayout
        {
            columns: 2
            rowSpacing: UM.Theme.getSize('default_lining').height
            columnSpacing: UM.Theme.getSize('default_margin').width
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignTop
 
            // Preset option
            UM.Label
            {
                text: 'Fan Tower Preset'
                MouseArea
                {
                    id: preset_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                Layout.fillWidth: true
                model: allow_customization ? dataModel.presetsModel.concat({'name': 'Custom'}) : dataModel.presetsModel
                textRole: 'name'
                currentIndex: dataModel.presetIndex

                onCurrentIndexChanged:
                {
                    dataModel.presetIndex = currentIndex
                }
            }

            // Towertype
            UM.Label
            {
                text: 'Tower Type'
                visible: show_custom_options
                MouseArea 
                {
                    id: tower_type_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                id: tower_type_selection
                Layout.fillWidth: true
                model: dataModel.towerTypesModel
                textRole: 'name'
                visible: show_custom_options
                currentIndex: dataModel.towerTypeIndex

                onCurrentIndexChanged: 
                {
                    dataModel.towerTypeIndex = currentIndex
                }
            }
            UM.ToolTip
            {
                text: 'The retraction chracteristic to change over the tower.<p>\'Distance\' changes the length of filament that is retracted or extruded.<p>\'Speed\' changes how quickly the filament is retracted or extruded.'
                visible: tower_type_mouse_area.containsMouse
            }

            // Starting value
            UM.Label 
            { 
                text: 'Starting ' + tower_type_selection.currentText 
                visible: show_custom_options
                MouseArea 
                {
                    id: starting_value_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.startValueStr
                visible: show_custom_options

                onTextChanged: 
                {
                    if (dataModel.startValueStr != text) dataModel.startValueStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The retraction value (speed or distance) for the first section of the tower.<p>For \'Distance\' towers, this is the length of filament retracted or extruded for each section.<p>For \'Speed\' towers, this is the speed at which the filament is retracted or extruded.'
                visible: starting_value_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: 'Ending ' + tower_type_selection.currentText
                visible: show_custom_options
                MouseArea 
                {
                    id: ending_value_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.endValueStr
                visible: show_custom_options

                onTextChanged:
                {
                    if (dataModel.endValueStr != text) dataModel.endValueStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The retraction value (speed or distance) for the last section of the tower.<p>For \'Distance\' towers, this is the length of filament retracted or extruded for each section.<p>For \'Speed\' towers, this is the speed at which the filament is retracted or extruded.'
                visible: ending_value_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: tower_type_selection.currentText + ' Change' 
                visible: show_custom_options
                MouseArea 
                {
                    id: value_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: dataModel.valueChangeStr
                visible: show_custom_options

                onTextChanged: 
                {
                    if (dataModel.valueChangeStr != text) dataModel.valueChangeStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The amount to change the retraction value (speed or distance) between tower sections.<p>In combination with the starting and ending values, this determines the number of sections in the tower.'
                visible: value_change_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: 'Tower Description' 
                visible: show_custom_options
                MouseArea 
                {
                    id: tower_description_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.fillWidth: true
                text: dataModel.towerDescription
                visible: show_custom_options

                onTextChanged: 
                {
                    if (dataModel.towerDescription != text) dataModel.towerDescription = text
                }
            }
            UM.ToolTip
            {
                text: 'An optional label to carve up the left side of the tower.<p>This can be used, for example, to identify the purpose of the tower or the material being printed.'
                visible: tower_description_mouse_area.containsMouse
            }
        }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: 'Cancel'
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: 'OK'
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        controller.dialogAccepted()
    }
}
