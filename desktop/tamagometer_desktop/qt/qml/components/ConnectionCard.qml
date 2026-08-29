import QtQuick
import QtQuick.Layouts
import "../theme" as AppTheme

Rectangle {
    default property alias content: contentLayout.data
    color: AppTheme.Theme.surface
    radius: 16
    border.color: AppTheme.Theme.border
    implicitHeight: contentLayout.implicitHeight + 36

    ColumnLayout {
        id: contentLayout
        anchors.fill: parent
        anchors.margins: 18
        spacing: 12
    }
}
