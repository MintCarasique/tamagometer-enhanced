import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Rectangle {
    property alias text: message.text
    color: AppTheme.Theme.accentSoft
    radius: 12
    implicitHeight: message.implicitHeight + 24
    border.color: AppTheme.Theme.border

    Label {
        id: message
        anchors.fill: parent
        anchors.margins: 12
        color: AppTheme.Theme.text
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
    }
}
