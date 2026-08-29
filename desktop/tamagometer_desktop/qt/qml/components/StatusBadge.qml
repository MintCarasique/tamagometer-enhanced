import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Rectangle {
    property string text: "Disconnected"
    implicitWidth: label.implicitWidth + 22
    implicitHeight: 30
    radius: 15
    color: AppTheme.Theme.accentSoft

    Label {
        id: label
        anchors.centerIn: parent
        text: parent.text
        color: AppTheme.Theme.accent
        font.weight: Font.DemiBold
    }
}
