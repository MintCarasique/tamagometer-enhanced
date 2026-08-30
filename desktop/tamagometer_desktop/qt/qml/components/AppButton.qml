import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Button {
    id: control
    property bool primary: false
    property string iconName: ""
    property bool iconFilled: false
    property bool iconOnly: false
    readonly property color resolvedTextColor: !enabled
        ? AppTheme.Theme.disabledText
        : ((primary || checked) ? "#FFFFFF" : AppTheme.Theme.text)

    implicitWidth: iconOnly ? 36 : Math.max(80, buttonContent.implicitWidth + leftPadding + rightPadding)
    implicitHeight: AppTheme.Theme.controlHeight
    leftPadding: 14
    rightPadding: 14
    opacity: 1

    contentItem: Item {
        Row {
            id: buttonContent
            anchors.centerIn: parent
            spacing: control.iconName.length > 0 && !control.iconOnly ? 7 : 0
            UiIcon {
                width: 17; height: 17
                visible: control.iconName.length > 0
                name: control.iconName
                filled: control.iconFilled
                color: control.resolvedTextColor
            }
            Text {
                visible: !control.iconOnly
                text: control.text
                font: control.font
                color: control.resolvedTextColor
                verticalAlignment: Text.AlignVCenter
            }
        }
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
