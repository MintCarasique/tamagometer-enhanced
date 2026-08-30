import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme
import "../components"

Popup {
    id: root
    objectName: "settingsDialog"
    required property var viewModel
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(parent.width - 32, 600)
    height: Math.min(parent.height - 32, 560)
    modal: true; focus: true; closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    onClosed: if (viewModel.settingsVisible) viewModel.closeSettings()
    background: Rectangle { color: AppTheme.Theme.surface; radius: 18; border.color: AppTheme.Theme.border }
    contentItem: ColumnLayout {
        Accessible.role: Accessible.Pane
        Accessible.name: "Tamagometer settings and About"
        spacing: 10
        Label { text: "Settings"; color: AppTheme.Theme.text; font.pixelSize: 24; font.weight: Font.DemiBold }
        AppSwitch {
            objectName: "autoConnectSwitch"
            text: "Connect automatically to a verified Flipper"
            checked: root.viewModel.autoConnect
            onToggled: root.viewModel.setAutoConnect(checked)
        }
        Label { Layout.fillWidth: true; text: "Automatic connection uses Flipper USB identity or a port that previously passed the Companion handshake."; color: AppTheme.Theme.muted; wrapMode: Text.WordWrap }
        AppSwitch {
            objectName: "reducedMotionSwitch"
            text: "Reduce nonessential motion"
            checked: root.viewModel.reducedMotion
            onToggled: root.viewModel.setReducedMotion(checked)
            Accessible.description: "Disables optional interface animation while preserving transfer progress."
        }
        AppButton { Layout.fillWidth: true; iconName: "refresh"; text: "Run setup again"; onClicked: root.viewModel.runSetupAgain() }
        AppButton { Layout.fillWidth: true; iconName: "diagnostics"; text: "Open diagnostics"; onClicked: { root.viewModel.closeSettings(); root.viewModel.openDiagnostics() } }
        Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: AppTheme.Theme.border }
        Label { text: "About"; color: AppTheme.Theme.text; font.pixelSize: 18; font.weight: Font.DemiBold }
        Label { Layout.fillWidth: true; text: "Tamagometer Enhanced Desktop " + root.viewModel.version + "\nRequires Tamagometer Enhanced Companion 2.0.0 or newer.\nIndependent enhanced fork of the MIT-licensed Tamagometer project. Unofficial and not affiliated with Bandai."; color: AppTheme.Theme.muted; wrapMode: Text.WordWrap }
        Item { Layout.fillHeight: true }
        AppButton { objectName: "settingsCloseButton"; Layout.alignment: Qt.AlignRight; iconName: "close"; text: "Close"; onClicked: root.viewModel.closeSettings() }
    }
}
