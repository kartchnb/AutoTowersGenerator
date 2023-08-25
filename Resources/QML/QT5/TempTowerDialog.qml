import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: 'Temperature Tower'

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

            // Starting temperature
            Label
            {
                text: 'Starting Temperature'
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.startTempStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.startTempStr != text) dataModel.startTempStr = text
                }
            }

            // Ending temperature
            Label
            {
                text: 'Ending Temperature'
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: dataModel.endTempStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.endTempStr != text) dataModel.endTempStr = text
                }
            }

            // Temperature change
            Label
            {
                text: 'Temperature Change'
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: dataModel.tempChangeStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.tempChangeStr != text) dataModel.tempChangeStr = text
                }
            }

            // Tower label
            Label
            {
                text: 'Tower Label'
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /.{0,3}/ }
                text: dataModel.towerLabel
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.towerLabel != text) dataModel.towerLabel = text
                }
            }

            // Tower description
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
