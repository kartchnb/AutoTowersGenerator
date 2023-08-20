import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: 'Temperature Tower'

    buttonSpacing: UM.Theme.getSize('default_margin').width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize('default_margin').height) + UM.Theme.getSize('button').height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

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
                source: Qt.resolvedUrl('../../Images/temptower_icon.png')
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

            // Start temp
            UM.Label
            {
                text: 'Starting Temperature'
                visible: show_custom_options
                MouseArea 
                {
                    id: starting_temperature_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.startTemperatureStr
                visible: show_custom_options

                onTextChanged:
                {
                    if (dataModel.startTemperatureStr != text) dataModel.startTemperatureStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The nozzle temperature for the first section of the tower.<p>It is good practice to make this temperature higher than the ending temperature.'
                visible: starting_temperature_mouse_area.containsMouse
            }

            // End temp
            UM.Label
            {
                text: 'Ending Temperature'
                visible: show_custom_options
                MouseArea 
                {
                    id: ending_temperature_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.endTemperatureStr
                visible: show_custom_options

                onTextChanged:
                {
                    if (dataModel.endTemperatureStr != text) dataModel.endTemperatureStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The nozzle temperature for the last section of the tower.<p>It is good practice to make this temperature lower than the starting temperature.'
                visible: ending_temperature_mouse_area.containsMouse
            }

            // Temp change
            UM.Label
            {
                text: 'Temperature Change'
                visible: show_custom_options
                MouseArea 
                {
                    id: temperature_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: dataModel.temperatureChangeStr
                visible: show_custom_options

                onTextChanged:
                {
                    if (dataModel.temperatureChangeStr != text) dataModel.temperatureChangeStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The amount to change the nozzle temperature between sections.<p>In combination with the starting and ending temperatures, this determines the number of sections in the tower.'
                visible: temperature_change_mouse_area.containsMouse
            }

            // Tower label
            UM.Label
            {
                text: 'Tower Label'
                visible: show_custom_options
                MouseArea 
                {
                    id: tower_label_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /.{0,4}/ }
                text: dataModel.towerLabel
                visible: show_custom_options

                onTextChanged:
                {
                    if (dataModel.towerLabel != text) dataModel.towerLabel = text
                }
            }
            UM.ToolTip
            {
                text: 'An optional short label to carve into the base of the right column of the tower.<p>This must be four characters or less.'
                visible: tower_label_mouse_area.containsMouse
            }

            // Tower description
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
