import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: 'Flow Tower'

    minimumWidth: screenScaleFactor * 500
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

        // Preset
        GridLayout
        {
            columns: 2
            rowSpacing: UM.Theme.getSize('default_lining').height
            columnSpacing: UM.Theme.getSize('default_margin').width
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignTop

            // Preset option
            Label
            {
                text: 'Preset'
            }
            ComboBox
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

            // The flow tower design
            Label 
            {
                text: 'Tower Design'
                visible: !dataModel.presetSelected
            }
            ComboBox
            {
                id: selected_tower_model
                Layout.fillWidth: true
                model: dataModel.towerDesignsModel
                textRole: 'name'
                visible: !dataModel.presetSelected
                currentIndex: dataModel.towerDesignIndex

                onCurrentIndexChanged:
                {
                    dataModel.towerDesignIndex = currentIndex
                }
            }

            // The starting flow rate
            Label
            { 
                text: 'Starting Flow %' 
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.startFlowPercentStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.startFlowPercentStr != text) dataModel.startFlowPercentStr = text
                }
            }

            // Ending flow rate
            Label 
            { 
                text: 'Ending Flow %' 
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.endFlowPercentStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.endFlowPercentStr != text) dataModel.endFlowPercentStr = text
                }
            }

            Label 
            { 
                text: 'Flow % Change' 
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: dataModel.flowPercentChangeStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.flowPercentChangeStr != text) dataModel.flowPercentChangeStr = text
                }
            }
    
            Label 
            { 
                text: 'Tower Label' 
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.fillWidth: true
                text: dataModel.towerLabel
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.towerLabel != text) dataModel.towerLabel = text
                }
            }
    
            Label 
            { 
                text: 'Tower Description' 
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.fillWidth: true
                text: dataModel.towerDescription
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.towerDescription != text) dataModel.towerDescription = text
                }
            }
        }
    }

    rightButtons: Button
    {
        text: 'OK'
        onClicked: dialog.accept()
    }

    leftButtons: Button
    {
        text: 'Cancel'
        onClicked: dialog.reject()
    }

    onAccepted:
    {
        controller.dialogAccepted()
    }
}
