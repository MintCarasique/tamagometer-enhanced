import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Button {
    id: control
    property bool primary: false
    readonly property color resolvedTextColor: !enabled
        ? AppTheme.Theme.disabledText
        : ((primary || checked) ? "#FFFFFF" : AppTheme.Theme.text)

    implicitHeight: 36
    leftPadding: 14
    rightPadding: 14
    opacity: 1

    contentItem: Text {
        text: control.text
        font: control.font
        color: control.resolvedTextColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: 7
        color: !control.enabled
            ? AppTheme.Theme.disabledSurface
            : ((control.primary || control.checked)
                ? (control.down ? Qt.darker(AppTheme.Theme.accent, 1.12) : AppTheme.Theme.accent)
                : (control.hovered ? AppTheme.Theme.controlHover : AppTheme.Theme.control))
        border.width: control.activeFocus ? 2 : 1
        border.color: control.activeFocus || control.primary || control.checked
            ? AppTheme.Theme.accent
            : AppTheme.Theme.border
    }
}
