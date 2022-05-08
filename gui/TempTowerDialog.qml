import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Temperature Tower"

    minimumWidth: screenScaleFactor * 455
    minimumHeight: screenScaleFactor * 300
    width: minimumWidth
    height: minimumHeight

    // Define the width of the text input text boxes
    property int numberInputWidth: screenScaleFactor * 100

    RowLayout
    {
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").width

        Rectangle
        {
            Layout.preferredWidth: icon.width
            Layout.fillHeight: true
            color: '#00017b'

            Image
            {
                id: icon
                source: "temptower_icon.png"
                anchors.verticalCenter: parent.verticalCenter
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

            Label
            {
                text: "Starting Temperature"
            }
            TextField
            {
                id: startTempInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startTemperatureStr
                onTextChanged: manager.startTemperatureStr = text
            }

            Label
            {
                text: "Ending Temperature"
            }
            TextField
            {
                id: endTempInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endTemperatureStr
                onTextChanged: manager.endTemperatureStr = text
            }

            Label
            {
                text: "Temperature Change"
            }
            TextField
            {
                id: tempChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.temperatureChangeStr
                onTextChanged: manager.temperatureChangeStr = text
            }

            Label
            {
                text: "Material Label"
            }
            TextField
            {
                id: materialLabelInput
                Layout.preferredWidth: numberInputWidth
                inputMask: "Xxxx"
                text: manager.materialLabelStr
                onTextChanged: manager.materialLabelStr = text
            }

            Label
            {
                text: "Tower Description"
            }
            TextField
            {
                id: towerDescriptionInput
                Layout.fillWidth: true
                text: manager.towerDescriptionStr
                onTextChanged: manager.towerDescriptionStr = text
            }
        }
    }

    rightButtons: Button
    {
        id: generateButton
        text: "Generate"
        onClicked: dialog.accept()
    }

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
