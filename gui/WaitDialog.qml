import QtQuick 2.11
import QtQuick.Controls 2.11

import UM 1.2 as UM

UM.Dialog
{
    id: dialog

property int screenScaleFactor: 1
    minimumWidth: screenScaleFactor * 322;
    minimumHeight: screenScaleFactor * 112;
    width: minimumWidth
    height: minimumHeight
    flags: Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint;
    title: "Generating Auto Tower"

    Row
    {
        spacing: 10
        height: dialog.height

        Image
        {
            source: "openscad.png"
        }

        Label
        {
            width: 200
            text: "Please wait while OpenSCAD generates the Auto Tower\n\nThis may take a few minutes"
            wrapMode: Text.Wrap
        }
    }
}
