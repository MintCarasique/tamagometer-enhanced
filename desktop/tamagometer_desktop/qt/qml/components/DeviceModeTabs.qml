pragma ComponentBehavior: Bound
import QtQuick

Flow {
    id: root
    property var modes: []
    property string currentMode: ""
    signal modeSelected(string key)
    spacing: 8

    Repeater {
        model: parent.modes
        delegate: AppButton {
            required property var modelData
            text: modelData.label
            checkable: true
            checked: modelData.key === root.currentMode
            onClicked: root.modeSelected(modelData.key)
            Accessible.name: text
            Accessible.description: checked ? "Current device mode" : "Switch device mode"
        }
    }
}
