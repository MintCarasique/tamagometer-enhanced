import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

Rectangle {
    id: root
    required property var viewModel
    property bool compact: false
    implicitHeight: compact ? 150 : 112
    color: AppTheme.Theme.accent

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: 14
        anchors.bottomMargin: 14
        anchors.leftMargin: 28
        anchors.rightMargin: 28

        RowLayout {
            Layout.fillWidth: true
            Label {
                Layout.fillWidth: true
                text: "Tamagometer Enhanced\n<span style='font-size:12px'>Desktop "
                    + root.viewModel.version + " · PySide6/QML</span>"
                textFormat: Text.RichText
                color: "white"
                font.pixelSize: root.compact ? 20 : 24
                font.weight: Font.DemiBold
            }
            StatusBadge {
                text: root.viewModel.connectionStatus
                Accessible.name: "Connection status: " + text
            }
        }

        Flow {
            Layout.fillWidth: true
            spacing: 8
            AppButton {
                objectName: "headerDiagnosticsButton"
                iconName: "diagnostics"
                text: "Diagnostics"
                onClicked: root.viewModel.openDiagnostics()
                Accessible.name: "Open diagnostics, Control D"
            }
            AppButton {
                objectName: "headerSettingsButton"
                iconName: "settings"
                text: "Settings"
                onClicked: root.viewModel.openSettings()
                Accessible.name: "Open settings, Control comma"
            }
            AppButton {
                objectName: "headerThemeButton"
                iconName: root.viewModel.darkTheme ? "sun" : "moon"
                text: root.viewModel.darkTheme ? "Light" : "Dark"
                onClicked: root.viewModel.toggleTheme()
                Accessible.name: "Toggle color theme"
            }
        }
    }
}
