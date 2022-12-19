import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Bed Level Pattern"

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
                source: Qt.resolvedUrl("../../Images/" + selectedBedLevelPattern.model[selectedBedLevelPattern.currentIndex]["icon"])
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
                text: "Bed Level Pattern Type"
            }
            ComboBox
            {
                id: selectedBedLevelPattern
                Layout.fillWidth: true
                model: manager.bedLevelPatternsModel
                textRole: "value"

                onCurrentIndexChanged: 
                {
                    manager.bedLevelPattern = model[currentIndex]["value"]
                }
            }

            Label
            {
                text: "Bed Fill %"
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[1-5]?[0-9]/ }
                text: manager.fillPercentageStr
                onTextChanged: if (manager.fillPercentageStr != text) manager.fillPercentageStr = text
            }

            Label
            {
                text: "Number of Rings"
                visible: manager.bedLevelPattern == "Concentric Squares" || manager.bedLevelPattern == "Concentric Circles"

             }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: manager.numberOfSquaresStr
                onTextChanged: if (manager.numberOfSquaresStr != text) manager.numberOfSquaresStr = text
                visible: manager.bedLevelPattern == "Concentric Squares" || manager.bedLevelPattern == "Concentric Circles"
            }

            Label
            {
                text: "Size in Cells"
                visible: manager.bedLevelPattern == "Grid" || manager.bedLevelPattern == "Padded Grid"
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: manager.cellSizeStr
                onTextChanged: if (manager.cellSizeStr != text) manager.cellSizeStr = text
                visible: manager.bedLevelPattern == "Grid" || manager.bedLevelPattern == "Padded Grid"
            }

            Label
            {
                text: "Pad Size"
                visible: manager.bedLevelPattern == "Padded Grid"
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: manager.padSizeStr
                onTextChanged: if (manager.padSizeStr != text) manager.padSizeStr = text
                visible: manager.bedLevelPattern == "Padded Grid"
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
