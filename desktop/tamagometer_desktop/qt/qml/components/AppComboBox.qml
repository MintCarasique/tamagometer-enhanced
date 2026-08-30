import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

ComboBox {
    id: control
    readonly property color resolvedBaseColor: AppTheme.Theme.surfaceAlt
    readonly property color resolvedIndicatorColor: enabled
        ? AppTheme.Theme.text
        : AppTheme.Theme.disabledText
    palette.base: resolvedBaseColor
    palette.window: AppTheme.Theme.surface
    palette.text: AppTheme.Theme.text
    palette.button: AppTheme.Theme.control
    palette.buttonText: AppTheme.Theme.text
    palette.highlight: AppTheme.Theme.accent
    palette.highlightedText: "#FFFFFF"
    palette.placeholderText: AppTheme.Theme.muted

    indicator: Text {
        x: control.width - width - control.rightPadding
        y: Math.round((control.height - height) / 2)
        text: "⌄"
        color: control.resolvedIndicatorColor
        font.pixelSize: 18
    }
}
