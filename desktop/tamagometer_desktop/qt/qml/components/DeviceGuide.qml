import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Item {
    id: root
    property bool friends: false
    property bool compact: false
    property bool active: false
    property int phase: 0
    readonly property real diagramWidth: Math.min(width, compact ? 190 : 270)
    implicitHeight: compact ? 38 : 112
    Accessible.role: Accessible.Graphic
    Accessible.name: friends ? "Tamagotchi back against the Flipper LF antenna"
        : "Tamagotchi IR window facing the Flipper IR window"

    Timer {
        interval: 180
        repeat: true
        running: root.active && root.visible && !AppTheme.Theme.reducedMotion
        onTriggered: root.phase = (root.phase + 1) % 3
    }
    Item {
        width: root.diagramWidth
        height: root.compact ? parent.height : 84
        anchors.horizontalCenter: parent.horizontalCenter
        DeviceIllustration {
            objectName: "guideTamagotchi"
            width: root.compact ? 32 : 62
            height: width
            x: root.friends ? parent.width * 0.37 : 3
            anchors.verticalCenter: parent.verticalCenter
            rotation: root.friends ? 0 : 90
            back: root.friends
            z: root.friends ? 2 : 0
        }
        DeviceIllustration {
            objectName: "guideFlipper"
            device: "flipper"
            width: root.compact ? 72 : 126
            height: root.compact ? 38 : 72
            x: root.friends ? parent.width * 0.37 - width / 2 + (root.compact ? 16 : 31)
                : parent.width - width - 3
            anchors.verticalCenter: parent.verticalCenter
            back: root.friends
        }
        Row {
            visible: !root.friends
            spacing: root.compact ? 3 : 6
            anchors.centerIn: parent
            anchors.horizontalCenterOffset: root.compact ? -12 : -27
            Repeater {
                model: 3
                Rectangle {
                    required property int index
                    width: root.compact ? 4 : 6
                    height: width
                    radius: width / 2
                    color: AppTheme.Theme.accent
                    opacity: !root.active || AppTheme.Theme.reducedMotion || index === root.phase ? 1 : 0.25
                }
            }
        }
    }
    Label {
        visible: !root.compact
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.friends ? "Back-to-back · LF antenna" : "Face the IR windows"
        color: AppTheme.Theme.muted
        font.pixelSize: 12
    }
}
