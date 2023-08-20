import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: 'Flow Tower'

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
                source: Qt.resolvedUrl('../../Images/' + dataModel.towerDesignIcon)
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
                id: selectedPreset
                Layout.fillWidth: true
                model: allow_customization ? dataModel.presetsModel.concat({'name': 'Custom'}) : dataModel.presetsModel
                textRole: 'name'
                currentIndex: dataModel.presetIndex

                onCurrentIndexChanged:
                {
                    dataModel.presetIndex = currentIndex
                }
            }

            // The flow tower design
            UM.Label
            {
                text: 'Tower Design'
                visible: show_custom_options
                MouseArea
                {
                    id: tower_design_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            Cura.ComboBox
            {
                Layout.fillWidth: true
                model: dataModel.towerDesignsModel
                textRole: 'name'
                visible: show_custom_options
                currentIndex: dataModel.towerDesignIndex

                onCurrentIndexChanged: 
                {
                    dataModel.towerDesignIndex = currentIndex
                }
            }
            UM.ToolTip
            {
                text: 'The tower model to use.<p>The \'Classic\' model is the same tower that is used by the temperature tower.<p>The \'Spiral\' model is radically different and may suit certain materials or uses better.<p>In the end, either one should work just fine.'
                visible: tower_design_mouse_area.containsMouse
            }

            // Starting flow percent
            UM.Label 
            { 
                text: 'Starting Flow %'
                visible: show_custom_options
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
                text: dataModel.startFlowPercentStr
                visible: show_custom_options

                onTextChanged: 
                {
                    if (dataModel.startFlowPercentStr != text) dataModel.startFlowPercentStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The flow rate % for the first section of the tower.<p>This is equivalent to changing Cura\'s \'Flow\' setting.<p>This value will be changed for each section of the tower<p>Rates less than 100 result in less filament being pushed through the nozzle.<p>Rates greater than 100 result in more filament being pushed through the nozzle.<p>It is good practice for the starting value to be higher than the ending value.'
                visible: start_flow_rate_mouse_area.containsMouse
            }

            // Ending flow percent
            UM.Label 
            { 
                text: 'Ending Flow Rate %' 
                visible: show_custom_options
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
                text: dataModel.endFlowPercentStr
                visible: show_custom_options

                onTextChanged: 
                {
                    if (dataModel.endFlowPercentStr != text) dataModel.endFlowPercentStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The flow rate % for the last section of the tower.<p>This is equivalent to changing Cura\'s \'Flow\' setting.<p>Rates less than 100 result in less filament being pushed through the nozzle.<p>Rates greater than 100 result in more filament being pushed through the nozzle.<p>It is good practice for the ending value to be lower than the starting value.'
                visible: end_flow_rate_mouse_area.containsMouse
            }

            // Flow percent change
            UM.Label 
            { 
                text: 'Flow Rate % Change' 
                visible: show_custom_options
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
                text: dataModel.flowPercentChangeStr
                visible: show_custom_options

                onTextChanged:
                {
                    if (dataModel.flowPercentChangeStr != text) dataModel.flowPercentChangeStr = text
                }
            }
            UM.ToolTip
            {
                text: 'The amount to change the flow rate % between sections of the tower.<p>In combination with the start end end flow rates, this determines the number of sections in the tower.'
                visible: flow_rate_change_mouse_area.containsMouse
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
