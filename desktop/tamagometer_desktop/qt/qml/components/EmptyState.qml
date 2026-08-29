import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

ColumnLayout {
    id: root
    property string title: "Nothing here yet"
    property string detail: "Try another category or search."
    spacing: 8

    Label {
        Layout.alignment: Qt.AlignHCenter
        text: root.title
        color: AppTheme.Theme.text
        font.pixelSize: 17
        font.weight: Font.DemiBold
    }
    Label {
        Layout.alignment: Qt.AlignHCenter
        Layout.maximumWidth: 360
        text: root.detail
        color: AppTheme.Theme.muted
        wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
    }
}
