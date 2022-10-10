import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "Retraction Tower"

    buttonSpacing: UM.Theme.getSize("default_margin").width
    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height) + UM.Theme.getSize("button").height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor("main_background")

    // Define the width of the number input text boxes
    property int numberInputWidth: UM.Theme.getSize("button").width

    RowLayout
    {
        id: contents
        width: dialog.width - 2 * UM.Theme.getSize("default_margin").width
        spacing: UM.Theme.getSize("default_margin").width

        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.preferredHeight: icon.height
            Layout.fillHeight: true
            color: UM.Theme.getColor("primary_button")

            Image
            {
                id: icon
                source: Qt.resolvedUrl("../../Images/retracttower_icon.png")
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        GridLayout
        {
            columns: 2
            rowSpacing: UM.Theme.getSize("default_lining").height
            columnSpacing: UM.Theme.getSize("default_margin").width
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignTop
 
            UM.Label
            {
                text: "Tower Type"
                MouseArea 
                {
                    id: tower_type_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                Layout.fillWidth: true
                model: manager.towerTypesModel
                textRole: "value"

                onCurrentIndexChanged: 
                {
                    manager.towerType = model[currentIndex]["value"]
                }
            }
            UM.ToolTip
            {
                text: "The retraction chracteristic to change over the tower.<p>\"Distance\" changes the length of filament that is retracted or extruded.<p>\"Speed\" changes how quickly the filament is retracted or extruded."
                visible: tower_type_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Starting Value" 
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
                text: manager.startValueStr
                onTextChanged: if (manager.startValueStr != text) manager.startValueStr = text
            }
            UM.ToolTip
            {
                text: "The retraction value for the first section of the tower.<p>For \"Distance\" towers, this is the length of filament retracted or extruded for each section.<p>For \"Speed\" towers, this is the speed at which the filament is retracted or extruded."
                visible: starting_value_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Ending Value" 
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
                text: manager.endValueStr
                onTextChanged: if (manager.endValueStr != text) manager.endValueStr = text
            }
            UM.ToolTip
            {
                text: "The retraction value for the last section of the tower.<p>For \"Distance\" towers, this is the length of filament retracted or extruded for each section.<p>For \"Speed\" towers, this is the speed at which the filament is retracted or extruded."
                visible: ending_value_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Value Change" 
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
                text: manager.valueChangeStr
                onTextChanged: if (manager.valueChangeStr != text) manager.valueChangeStr = text
            }
            UM.ToolTip
            {
                text: "The amount to change the retraction value between tower sections.<p>In combination with the starting and ending values, this determines the number of sections in the tower."
                visible: value_change_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Tower Description" 
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
                text: manager.towerDescriptionStr
                onTextChanged: if (manager.towerDescriptionStr != text) manager.towerDescriptionStr = text
            }
            UM.ToolTip
            {
                text: "An optional label to carve up the left side of the tower.<p>This can be used, for example, to identify the purpose of the tower or the material being printed."
                visible: tower_description_mouse_area.containsMouse
            }
        }
    }

    rightButtons: 
    [
        Cura.SecondaryButton
        {
            text: "Cancel"
            onClicked: dialog.reject()
        },
        Cura.PrimaryButton
        {
            text: "OK"
            onClicked: dialog.accept()
        }
    ]

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
