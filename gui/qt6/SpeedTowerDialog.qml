// This dialog is a placeholder for when I get around to incorporating a speed tower
import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM
import Cura 1.7 as Cura

UM.Dialog
{
    id: dialog
    title: "Speed Tower"

    minimumWidth: screenScaleFactor * 425;
    minimumHeight: screenScaleFactor * 300;
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
                source: "../speedtower_icon.png"
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
                text: "Speed Type to Control" 
            }
            ComboBox 
            {
                id: speedTypeInput
                model: ["acceleration", "jerk", "junction", "Marlin linear", "RepRap pressure"]
            }

            UM.Label 
            { 
                text: "Starting Speed" 
            }
            Cura.TextField
            {
                id: startSpeedInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: "8"
            }

            UM.Label 
            { 
                text: "Ending Speed" 
            }
            Cura.TextField
            {
                id: endSpeedInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[0-9]*(\.[0-9]+)?/ }
                text: "32"
            }

            UM.Label 
            { 
                text: "Speed Change" 
            }
            Cura.TextField
            {
                id: speedChangeInput
                Layout.preferredWidth: numberInputWidth
                validator: RegularExpressionValidator { regularExpression: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: "4"
            }
    
            UM.Label 
            { 
                text: "Tower Description" 
            }
            Cura.TextField
            {
                id: towerDescriptionInput
                Layout.fillWidth: true
                text: ""
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
