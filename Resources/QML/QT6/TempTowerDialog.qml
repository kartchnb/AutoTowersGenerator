import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
	
	property variant catalog: UM.I18nCatalog { name: "autotowers" }
	
    title: catalog.i18nc("@title", "Temperature Tower")
	
    buttonSpacing: UM.Theme.getSize('default_margin').width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize('default_margin').height) + UM.Theme.getSize('button').height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    // Define the width of the number input text boxes
    property int numberInputWidth: UM.Theme.getSize('button').width


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
                source: Qt.resolvedUrl('../../Images/' + dataModel.dialogIcon)
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
                text: catalog.i18nc("@label", "Temp Tower Preset")
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
                model: enableCustom ? dataModel.presetsModel.concat({'name': catalog.i18nc("@model", "Custom")}) : dataModel.presetsModel
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
                text: catalog.i18nc("@label", "Starting Temperature")
                visible: !dataModel.presetSelected
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
                text: dataModel.startTempStr
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.startTempStr != text) dataModel.startTempStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The nozzle temperature for the first section of the tower.<p>It is good practice to make this temperature higher than the ending temperature.")
                visible: starting_temperature_mouse_area.containsMouse
            }

            // End temp
            UM.Label
            {
                text: catalog.i18nc("@label", "Ending Temperature")
                visible: !dataModel.presetSelected
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
                text: dataModel.endTempStr
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.endTempStr != text) dataModel.endTempStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The nozzle temperature for the last section of the tower.<p>It is good practice to make this temperature lower than the starting temperature.")
                visible: ending_temperature_mouse_area.containsMouse
            }

            // Temp change
            UM.Label
            {
                text: catalog.i18nc("@label", "Temperature Change")
                visible: !dataModel.presetSelected
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
                text: dataModel.tempChangeStr
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.tempChangeStr != text) dataModel.tempChangeStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The amount to change the nozzle temperature between sections.<p>In combination with the starting and ending temperatures, this determines the number of sections in the tower.")
                visible: temperature_change_mouse_area.containsMouse
            }

            // Tower label
            UM.Label
            {
                text: catalog.i18nc("@label", "Tower Label")
                visible: !dataModel.presetSelected
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
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.towerLabel != text) dataModel.towerLabel = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "An optional short label to carve into the base of the right column of the tower.<p>This must be four characters or less.")
                visible: tower_label_mouse_area.containsMouse
            }

            // Tower description
            UM.Label
            {
                text: catalog.i18nc("@label", "Tower Description")
                visible: !dataModel.presetSelected
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
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.towerDescription != text) dataModel.towerDescription = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "An optional label to carve up the left side of the tower.<p>This can be used, for example, to identify the purpose of the tower or the material being printed.")
                visible: tower_description_mouse_area.containsMouse
            }
       }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: catalog.i18nc("@button", "Cancel")
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: catalog.i18nc("@button", "OK")
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        controller.dialogAccepted()
    }

}
