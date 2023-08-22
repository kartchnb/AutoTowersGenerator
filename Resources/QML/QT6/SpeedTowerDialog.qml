import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: 'Speed Tower'

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
                text: 'Preset'
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

            // Tower type option
            UM.Label
            {
                text: 'Tower Type'
                visible: !dataModel.presetSelected
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
                model: dataModel.towerTypesModel
                textRole: 'name'
                visible: !dataModel.presetSelected
                currentIndex: dataModel.towerTypeIndex

                onCurrentIndexChanged: 
                {
                    dataModel.towerTypeIndex = currentIndex
                }
            }
            UM.ToolTip
            {
                text: 'The type of speed to vary across the tower.<p>"Print Speed" towers change the speed at which the nozzle moves while printing (equivalent to Cura\'s "print speed" setting).<p>"Acceleration" changes how fast the nozzle accelerates during printing.<p>The other towers are more specialized.'
                visible: tower_type_mouse_area.containsMouse
            }

            // Start speed
            UM.Label 
            { 
                text: 'Starting Speed' 
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: starting_speed_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.startSpeedStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.startSpeedStr != text) dataModel.startSpeedStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The speed value for the first section of the tower.'
                visible: starting_speed_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: 'Ending Speed' 
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: ending_speed_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.endSpeedStr
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.endSpeedStr != text) dataModel.endSpeedStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The speed value for the last section of the tower.'
                visible: ending_speed_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: 'Speed Change' 
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: speed_change_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: dataModel.speedChangeStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.speedChangeStr != text) dataModel.speedChangeStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The amount to change the speed between tower sections.<p>In combination with the starting and ending values, this determines the number of sections in the tower.'
                visible: speed_change_mouse_area.containsMouse
            }

            UM.Label 
            { 
                text: 'Wing Length' 
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: wing_length_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: dataModel.wingLengthStr
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.wingLengthStr != text) dataModel.wingLengthStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The length of each "wing" of the tower. Longer wings allow more time for the printer to get up to speed while printing, but results in more material being used.'
                visible: wing_length_mouse_area.containsMouse
            }
    
            UM.Label 
            { 
                text: 'Tower Label' 
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: tower_label_mouse_Area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.TextField
            {
                Layout.fillWidth: true
                text: dataModel.towerLabel
                visible: !dataModel.presetSelected

                onTextChanged:
                {
                    if (dataModel.towerLabel != text) dataModel.towerLabel = text
                }
            }
            UM.ToolTip
            {
                text: 'An optional label to carve into the base of the tower.<p>This can be used, for example, to identify the purpose of the tower or the material being printed.'
                visible: tower_label_mouse_Area.containsMouse
            }
    
            UM.Label 
            { 
                text: 'Tower Description' 
                visible: !dataModel.presetSelected
                MouseArea 
                {
                    id: description_label_mouse_area
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
                text: 'An optional second description to carve into the base of the tower.<p>This is can be used to provide additional information about the tower - why you printed it, for instance.'
                visible: description_label_mouse_area.containsMouse
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
