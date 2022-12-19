import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "Flow Tower"

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
                source: Qt.resolvedUrl("../../Images/flowtower_icon.png")
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
                text: "Starting Flow Rate %" 
                MouseArea 
                {
                    id: start_flow_rate_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startFlowStr
                onTextChanged: if (manager.startFlowStr != text) manager.startFlowStr = text
            }
            UM.ToolTip
            {
                text: "The flow rate % for the first section of the tower.<p>This is equivalent to changing Cura's \"Flow\" setting.<p>This value will be changed for each section of the tower<p>Rates less than 100 result in less filament being pushed through the nozzle.<p>Rates greater than 100 result in more filament being pushed through the nozzle.<p>It is good practice for the starting value to be higher than the ending value."
                visible: start_flow_rate_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Ending Flow Rate %" 
                MouseArea 
                {
                    id: end_flow_rate_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endFlowStr
                onTextChanged: if (manager.endFlowStr != text) manager.endFlowStr = text
            }
            UM.ToolTip
            {
                text: "The flow rate % for the last section of the tower.<p>This is equivalent to changing Cura's \"Flow\" setting.<p>Rates less than 100 result in less filament being pushed through the nozzle.<p>Rates greater than 100 result in more filament being pushed through the nozzle.<p>It is good practice for the ending value to be lower than the starting value."
                visible: end_flow_rate_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Flow Rate % Change" 
                MouseArea 
                {
                    id: flow_rate_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.flowChangeStr
                onTextChanged: if (manager.flowChangeStr != text) manager.flowChangeStr = text
            }
            UM.ToolTip
            {
                text: "The amount to change the flow rate % between sections of the tower.<p>In combination with the start end end flow rates, this determines the number of sections in the tower."
                visible: flow_rate_change_mouse_area.containsMouse
            }
   
            UM.Label
            {
                text: "Tower Label"
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
                text: manager.towerLabelStr
                onTextChanged: if (manager.towerLabelStr != text) manager.towerLabelStr = text
            }
            UM.ToolTip
            {
                text: "An optional short label to carve into the base of the right column of the tower.<p>This must be four characters or less."
                visible: tower_label_mouse_area.containsMouse
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
