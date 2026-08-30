import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

ComboBox {
    id: control
    implicitHeight: AppTheme.Theme.controlHeight
    readonly property color resolvedBaseColor: AppTheme.Theme.surfaceAlt
    readonly property color resolvedIndicatorColor: enabled
        ? AppTheme.Theme.text
        : AppTheme.Theme.disabledText
    readonly property color resolvedBorderColor: activeFocus
        ? AppTheme.Theme.accent
        : AppTheme.Theme.borderStrong
    palette.base: resolvedBaseColor
    palette.window: AppTheme.Theme.surface
    palette.text: AppTheme.Theme.text
    palette.button: AppTheme.Theme.control
    palette.buttonText: AppTheme.Theme.text
    palette.highlight: AppTheme.Theme.accent
    palette.highlightedText: "#FFFFFF"
    palette.placeholderText: AppTheme.Theme.muted

    indicator: UiIcon {
        x: control.width - width - control.rightPadding
        y: Math.round((control.height - height) / 2)
        width: 18; height: 18
        name: "chevron-down"
        color: control.resolvedIndicatorColor
    }

    background: Rectangle {
        radius: 6
        color: AppTheme.Theme.control
        border.width: control.activeFocus ? 2 : 1
        border.color: control.resolvedBorderColor
    }
}
