import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
	
	property variant catalog: UM.I18nCatalog { name: "autotowers" }
	
    title: catalog.i18nc("@title", "Fan Tower")

    buttonSpacing: UM.Theme.getSize('default_margin').width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize('default_margin').height) + UM.Theme.getSize('button').height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor('main_background')

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
                text: catalog.i18nc("@label", "Fan Tower Preset")
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
                model: enableCustom ? dataModel.presetsModel.concat({'name': 'Custom'}) : dataModel.presetsModel
                textRole: 'name'
                currentIndex: dataModel.presetIndex

                onCurrentIndexChanged:
                {
                    dataModel.presetIndex = currentIndex
                }
            }

            // Starting fan percent
            UM.Label 
            { 
                text: catalog.i18nc("@label", "Starting Fan Speed %")
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: starting_fan_percent_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]{1,2}(?:\.[0-9]+)?|100/ }
                text: dataModel.startFanPercentStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.startFanPercentStr != text) dataModel.startFanPercentStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The fan speed % for the first section of the tower.<p>This value will be changed for each section of the tower.<p>This should be a value between 0 and 100.")
                visible: starting_fan_percent_mouse_area.containsMouse
            }

            // Ending fan percent
            UM.Label 
            { 
                text: catalog.i18nc("@label", "Ending Fan Speed %")
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: ending_fan_percent_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]{1,2}(?:\.[0-9]+)?|100/ }
                text: dataModel.endFanPercentStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.endFanPercentStr != text) dataModel.endFanPercentStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The fan speed % for the last section of the tower.<p>This should be a value between 0 and 100.")
                visible: ending_fan_percent_mouse_area.containsMouse
            }

            // Fan percent change
            UM.Label 
            { 
                text: catalog.i18nc("@label", "Fan Speed % Change")
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: fan_speed_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]{1,2}(?:\.[0-9]+)?|[+-]?100/ }
                text: dataModel.fanPercentChangeStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.fanPercentChangeStr != text) dataModel.fanPercentChangeStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "The amount to change the fan speed % between sections of the tower.<p>In combination with the start end end fan speed %, this determines the number of sections in the tower.")
                visible: fan_speed_change_mouse_area.containsMouse
            }

            // The tower label
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
                text: dataModel.towerLabelStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.towerLabelStr != text) dataModel.towerLabelStr = text
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
                    if (dataModel.towerDescriptionStr != text) dataModel.towerDescriptionStr = text
                }
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@tooltip", "An optional label to carve up the left side of the tower.<p>This can be used, for example, to identify the purpose of the tower or the material being printed.")
                visible: tower_description_mouse_area.containsMouse
            }

            // Maintain fan value for bridges
            UM.Label
            {
                text: catalog.i18nc("@label", "Maintain Value for Bridges")
                MouseArea 
                {
                    id: maintain_bridge_value_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            UM.CheckBox
            {
                id: maintainBridgeValueCheckBox
                checked: dataModel.maintainBridgeValue
                onClicked: dataModel.maintainBridgeValue = checked
            }
            UM.ToolTip
            {
                text: catalog.i18nc("@label", "Selects whether the fan speed % for the current section is maintained while bridges are being printed.")
                visible: maintain_bridge_value_mouse_area.containsMouse
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
