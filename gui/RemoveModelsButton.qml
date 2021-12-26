import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

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
    iconSource: "AutoTowers Icon.svg"
    visible: manager.autoTowerGenerated
    fixedWidthMode: false
}
