import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Speed Tower"

    minimumWidth: screenScaleFactor * 445
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize("default_margin").height) + UM.Theme.getSize("button").height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

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
                source: Qt.resolvedUrl("../../Images/speedtower_icon.png")
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

            Label
            {
                text: "Tower Type"
            }
            ComboBox
            {
                Layout.fillWidth: true
                model: manager.towerTypesModel
                textRole: "value"

                onCurrentIndexChanged: 
                {
                    manager.towerType = model[currentIndex]["value"]
                }
            }

            Label 
            { 
                text: "Starting Speed" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.startSpeedStr
                onTextChanged: if (manager.startSpeedStr != text) manager.startSpeedStr = text
            }

            Label 
            { 
                text: "Ending Speed" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*(\.[0-9]+)?/ }
                text: manager.endSpeedStr
                onTextChanged: if (manager.endSpeedStr != text) manager.endSpeedStr = text
            }

            Label 
            { 
                text: "Speed Change" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.speedChangeStr
                onTextChanged: if (manager.speedChangeStr != text) manager.speedChangeStr = text
            }

            Label 
            { 
                text: "Wing Length" 
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[+-]?[0-9]*(\.[0-9]+)?/ }
                text: manager.wingLengthStr
                onTextChanged: if (manager.wingLengthStr != text) manager.wingLengthStr = text
            }
    
            Label 
            { 
                text: "Tower Label" 
            }
            TextField
            {
                Layout.fillWidth: true
                text: manager.towerLabelStr
                onTextChanged: if (manager.towerLabelStr != text) manager.towerLabelStr = text
            }
    
            Label 
            { 
                text: "Tower Description" 
            }
            TextField
            {
                Layout.fillWidth: true
                text: manager.descriptionLabelStr
                onTextChanged: if (manager.descriptionLabelStr != text) manager.descriptionLabelStr = text
            }
        }
    }

    rightButtons: Button
    {
        text: "OK"
        onClicked: dialog.accept()
    }

    leftButtons: Button
    {
        text: "Cancel"
        onClicked: dialog.reject()
    }

    onAccepted:
    {
        manager.dialogAccepted()
    }
}
