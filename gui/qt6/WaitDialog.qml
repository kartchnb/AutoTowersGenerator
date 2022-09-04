import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

import UM 1.6 as UM

UM.Dialog
{
    id: dialog
    title: "Generating Auto Tower"

    minimumWidth: screenScaleFactor * 500;
    minimumHeight: screenScaleFactor * 112;
    width: minimumWidth
    height: minimumHeight
    flags: Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint;

    RowLayout
    {
        spacing: UM.Theme.getSize("default_margin").width
        Layout.fillHeight: true
        Layout.fillWidth: true

        Image
        {
            source: "openscad.png"
        }
        Label
        {
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: "Please wait while OpenSCAD generates the Auto Tower\n\nThis may take a few minutes"
            wrapMode: Text.Wrap
        }
    }
}
