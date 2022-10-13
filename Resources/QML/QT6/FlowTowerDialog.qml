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
                text: manager.startValueStr
                onTextChanged: if (manager.startValueStr != text) manager.startValueStr = text
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
                text: manager.endValueStr
                onTextChanged: if (manager.endValueStr != text) manager.endValueStr = text
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
                text: manager.valueChangeStr
                onTextChanged: if (manager.valueChangeStr != text) manager.valueChangeStr = text
            }
            UM.ToolTip
            {
                text: "The amount to change the flow rate % between sections of the tower.<p>In combination with the start end end flow rates, this determines the number of sections in the tower."
                visible: flow_rate_change_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Section Size" 
                MouseArea 
                {
                    id: section_size_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.sectionSizeStr
                onTextChanged: if (manager.sectionSizeStr != text) manager.sectionSizeStr = text
            }
            UM.ToolTip
            {
                text: "The size (width, depth, and height) of each section. This can be used to detect flow problems by measuring the dimensions of each section after the tower has been printed."
                visible: section_size_change_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: "Section Hole Diameter" 
                MouseArea 
                {
                    id: section_hole_diameter_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.sectionHoleDiameterStr
                onTextChanged: if (manager.sectionHoleDiameterStr != text) manager.sectionHoleDiameterStr = text
            }
            UM.ToolTip
            {
                text: "The diameter of the holes in each tower section. This can be used to detect flow problems by measuring the diameter of the hole in each section after the tower has been printed"
                visible: section_hole_diameter_change_mouse_area.containsMouse
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
                Layout.fillWidth: true
                text: manager.towerLabelStr
                onTextChanged: if (manager.towerLabelStr != text) manager.towerLabelStr = text
            }
            UM.ToolTip
            {
                text: "An optional label to carve into the base of the tower.<p>This can be used, for example, to identify the purpose of the tower or the material being printed."
                visible: tower_label_mouse_area.containsMouse
            }
    
            UM.Label 
            { 
                text: "Temperature Label" 
                MouseArea 
                {
                    id: temperature_label_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.fillWidth: true
                text: manager.temperatureLabelStr
                onTextChanged: if (manager.temperatureLabelStr != text) manager.temperatureLabelStr = text
            }
            UM.ToolTip
            {
                text: "An optional secondary label to carve into the base of the tower.<p>This is intended to be used to indicate the temperature at which the tower was printed, but can be used for other purposes as well."
                visible: temperature_label_mouse_area.containsMouse
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
