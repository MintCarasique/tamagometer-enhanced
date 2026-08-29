pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Flow {
    id: root
    property var modes: []
    property string currentMode: ""
    signal modeSelected(string key)
    spacing: 8

    Repeater {
        model: parent.modes
        delegate: Button {
            required property var modelData
            text: modelData.label
            checkable: true
            checked: modelData.key === root.currentMode
            onClicked: root.modeSelected(modelData.key)
            palette.button: checked ? AppTheme.Theme.accent : AppTheme.Theme.surface
            palette.buttonText: checked ? "white" : AppTheme.Theme.text
            Accessible.name: text
            Accessible.description: checked ? "Current device mode" : "Switch device mode"
        }
    }
}
