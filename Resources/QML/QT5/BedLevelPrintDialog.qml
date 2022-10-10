import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: "Bed Level Print"

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
                source: Qt.resolvedUrl("../../Images/" + selectedBedLevelPrintType.model[selectedBedLevelPrintType.currentIndex]["icon"])
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
                text: "Bed Level Print Type"
                MouseArea 
                {
                    id: bed_level_print_type_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
            }
            ComboBox
            {
                id: selectedBedLevelPrintType
                Layout.fillWidth: true
                model: manager.bedLevelPrintTypesModel
                textRole: "value"

                onCurrentIndexChanged: 
                {
                    manager.bedLevelPrintType = model[currentIndex]["value"]
                }
            }

            Label
            {
                text: "Bed Fill %"
                MouseArea 
                {
                    id: bed_inset_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
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
                text: "Number of Squares"
                visible: manager.bedLevelPrintType == "Concentric Squares"
                MouseArea 
                {
                    id: number_of_squares_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
             }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: manager.numberOfSquaresStr
                onTextChanged: if (manager.numberOfSquaresStr != text) manager.numberOfSquaresStr = text
                visible: manager.bedLevelPrintType == "Concentric Squares"
            }

            Label
            {
                text: "Size in Cells"
                visible: manager.bedLevelPrintType == "Grid"
                MouseArea 
                {
                    id: size_in_cells_mouse_area
                    anchors.fill: parent
                    hoverEnabled: true
                }
             }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: manager.cellSizeStr
                onTextChanged: if (manager.cellSizeStr != text) manager.cellSizeStr = text
                visible: manager.bedLevelPrintType == "Grid"
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
