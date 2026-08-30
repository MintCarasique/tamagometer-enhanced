import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Switch {
    id: control
    readonly property color resolvedTrackColor: checked
        ? AppTheme.Theme.accent
        : AppTheme.Theme.disabledSurface

    spacing: 10
    opacity: enabled ? 1 : 0.65

    indicator: Rectangle {
        implicitWidth: 44
        implicitHeight: 24
        x: control.leftPadding
        y: Math.round((control.height - height) / 2)
        radius: height / 2
        color: control.resolvedTrackColor
        border.width: 1
        border.color: control.checked ? AppTheme.Theme.accent : AppTheme.Theme.borderStrong

        Rectangle {
            width: 18
            height: 18
            radius: 9
            y: 3
            x: control.checked ? parent.width - width - 3 : 3
            color: control.checked ? "#FFFFFF" : AppTheme.Theme.muted
        }
    }

    contentItem: Text {
        leftPadding: control.indicator.width + control.spacing
        text: control.text
        font: control.font
        color: control.enabled ? AppTheme.Theme.text : AppTheme.Theme.disabledText
        verticalAlignment: Text.AlignVCenter
        wrapMode: Text.WordWrap
    }
}
