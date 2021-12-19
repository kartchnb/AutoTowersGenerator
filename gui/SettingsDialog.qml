import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

    minimumWidth: screenScaleFactor * 280;
    minimumHeight: screenScaleFactor * 120;
    width: minimumWidth
    height: minimumHeight

    // Create aliases to allow easy access to each of the parameters
    property alias openScadPath : openscadCommandInput.text

    GridLayout
    {
        id: gridLayout

        columns: 2

        Label { text: "OpenSCAD Path" }

        TextField
        {
            id: openscadCommandInput
            text: ""
            width: 300
        }

        Column
        {
            Button
            {
                text: "Clear STL Cache"
                onClicked: manager.clearCachedStls()
            }
        }
    }

    leftButtons: Button
    {
        id: okButton
        text: "OK"
        onClicked: dialog.accept()
    }

    rightButtons: Button
    {
        id: cancelButton
        text: "Cancel"
        onClicked: dialog.reject()
    }

    onAccepted:
    {
        manager.settingsDialogAccepted()
    }

}
