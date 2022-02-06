import QtQuick 2.11
import QtQuick.Controls 2.11
import QtQuick.Layouts 1.11

import UM 1.2 as UM
import Cura 1.0 as Cura

Cura.SecondaryButton
{
    height: UM.Theme.getSize("action_button").height
    tooltip:
    {
        var tipText = "Remove AutoTower Model";
        return tipText
    }
    toolTipContentAlignment: Cura.ToolTip.ContentAlignment.AlignLeft
    onClicked: manager.removeButtonClicked()
    iconSource: "AutoTowers Icon.png"
    visible: manager.autoTowerGenerated
    fixedWidthMode: false
}
