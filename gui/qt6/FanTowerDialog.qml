import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "Fan Tower"

    minimumWidth: screenScaleFactor * 445;
    minimumHeight: screenScaleFactor * 245;
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor("main_background")

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
            color: "#00017b"

            Image
            {
                id: icon
                source: "../fantower_icon.png"
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
                text: "Starting Fan Percent" 
            }
            Cura.TextField
            {
                id: startPercentInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startPercentStr
                onTextChanged: if (manager.startPercentStr != text) manager.startPercentStr = text
            }

            UM.Label 
            { 
                text: "Ending Fan Percent" 
            }
            Cura.TextField
            {
                id: endPercentInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endPercentStr
                onTextChanged: if (manager.endPercentStr != text) manager.endPercentStr = text
            }

            UM.Label 
            { 
                text: "Fan Speed Change" 
            }
            Cura.TextField
            {
                id: percentChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.percentChangeStr
                onTextChanged: if (manager.percentChangeStr != text) manager.percentChangeStr = text
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
