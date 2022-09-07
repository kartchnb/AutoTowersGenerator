import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

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
                source: "../temptower_icon.png"
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

            UM.Label
            {
                text: "Starting Temperature"
            }
            Cura.TextField
            {
                id: startTempInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startTemperatureStr
                onTextChanged: if (manager.startTemperatureStr != text) manager.startTemperatureStr = text
            }

            UM.Label
            {
                text: "Ending Temperature"
            }
            Cura.TextField
            {
                id: endTempInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endTemperatureStr
                onTextChanged: if (manager.endTemperatureStr != text) manager.endTemperatureStr = text
            }

            UM.Label
            {
                text: "Temperature Change"
            }
            Cura.TextField
            {
                id: tempChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.temperatureChangeStr
                onTextChanged: if (manager.temperatureChangeStr != text) manager.temperatureChangeStr = text
            }

            UM.Label
            {
                text: "Material Label"
            }
            Cura.TextField
            {
                id: labelInput
                Layout.preferredWidth: numberInputWidth
                inputMask: "xxxx"
                text: manager.materialLabelStr
                onTextChanged: if (manager.materialLabelStr != text) manager.materialLabelStr = text
            }

            UM.Label
            {
                text: "Tower Description"
            }
            Cura.TextField
            {
                id: towerDescriptionInput
                Layout.fillWidth: true
                text: manager.towerDescriptionStr
                onTextChanged: if (manager.towerDescriptionStr != text) manager.towerDescriptionStr = text
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
