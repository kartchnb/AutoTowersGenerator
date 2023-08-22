import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog
    title: 'Bed Level Pattern'

    minimumWidth: screenScaleFactor * 500
    minimumHeight: (screenScaleFactor * contents.childrenRect.height) + (2 * UM.Theme.getSize('default_margin').height) + UM.Theme.getSize('button').height
    maximumHeight: minimumHeight
    width: minimumWidth
    height: minimumHeight

    backgroundColor: UM.Theme.getColor('main_background')

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

            // Bed level pattern option
            Label
            {
                text: 'Bed Level Pattern Type'
                visible: !dataModel.presetSelected
            }
            ComboBox
            {
                id: selected_pattern
                Layout.fillWidth: true
                model: dataModel.patternsModel
                textRole: 'name'
                visible: !dataModel.presetSelected
                currentIndex: dataModel.patternIndex

                onCurrentIndexChanged: 
                {
                    dataModel.patternIndex = currentIndex
                }
            }

            // Bed fill %
            Label
            {
                text: 'Bed Fill %'
                visible: !dataModel.presetSelected
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[1-5]?[0-9]/ }
                text: dataModel.fillPercentageStr
                visible: !dataModel.presetSelected

                onTextChanged: 
                {
                    if (dataModel.fillPercentageStr != text) dataModel.fillPercentageStr = text
                }
            }

            // Number of rings
            Label
            {
                text: 'Number of Rings'
                visible: !dataModel.presetSelected && (selected_pattern.currentText == 'Spiral Squares' || selected_pattern.currentText == 'Concentric Squares' || selected_pattern.currentText == 'Concentric Circles')

             }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: dataModel.numberOfRingsStr
                visible: !dataModel.presetSelected && (selected_pattern.currentText == 'Spiral Squares' || selected_pattern.currentText == 'Concentric Squares' || selected_pattern.currentText == 'Concentric Circles')
                
                onTextChanged: 
                {
                    if (dataModel.numberOfRingsStr != text) dataModel.numberOfRingsStr = text
                }
            }

            // Size in cells
            Label
            {
                text: 'Size in Cells'
                visible: !dataModel.presetSelected && (selected_pattern.currentText == 'Grid' || selected_pattern.currentText == 'Padded Grid')
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: dataModel.cellSizeStr
                visible: !dataModel.presetSelected && (selected_pattern.currentText == 'Grid' || selected_pattern.currentText == 'Padded Grid')

                onTextChanged: 
                {
                    if (dataModel.cellSizeStr != text) dataModel.cellSizeStr = text
                }
            }

            // Pad size
            Label
            {
                text: 'Pad Size'
                visible: !dataModel.presetSelected && (selected_pattern.currentText == 'Padded Grid')
            }
            TextField
            {
                Layout.preferredWidth: numberInputWidth
                validator: RegExpValidator { regExp: /[0-9]*/ }
                text: dataModel.padSizeStr
                visible: !dataModel.presetSelected && (selected_pattern.currentText == 'Padded Grid')

                onTextChanged:
                {
                    if (dataModel.padSizeStr != text) dataModel.padSizeStr = text
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
