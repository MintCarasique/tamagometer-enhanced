import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

ScrollBar {
    id: control
    padding: 2
    minimumSize: 0.08

    contentItem: Rectangle {
        implicitWidth: 10
        implicitHeight: 10
        radius: 5
        color: control.pressed ? AppTheme.Theme.accent : AppTheme.Theme.muted
        opacity: control.policy === ScrollBar.AlwaysOn || control.active ? 0.72 : 0.42
    }

    background: Rectangle {
        color: "transparent"
    }
}
