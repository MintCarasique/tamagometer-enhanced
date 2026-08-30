import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    property alias text: label.text
    property alias color: label.color
    property alias fontPixelSize: label.font.pixelSize
    property alias fontWeight: label.font.weight
    Layout.fillWidth: true

    Label {
        id: label
        anchors.fill: parent
        wrapMode: Text.WordWrap
        verticalAlignment: Text.AlignVCenter
    }
}
