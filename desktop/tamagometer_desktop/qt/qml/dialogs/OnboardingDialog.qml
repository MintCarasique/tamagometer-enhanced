import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

Popup {
    id: root
    required property var viewModel
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(parent.width - 32, 620)
    height: Math.min(parent.height - 32, 480)
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape
    onClosed: if (viewModel.onboardingVisible) viewModel.closeOnboarding()
    background: Rectangle { color: AppTheme.Theme.surface; radius: 18; border.color: AppTheme.Theme.border }

    property var titles: ["Welcome to Tamagometer Enhanced", "Install and open the Companion", "Connect automatically"]
    property var bodies: [
        "This setup checks that Desktop can find your Flipper and matching Companion. No account or personal information is required.",
        "Copy tamagometer_enhanced.fap to SD Card/apps/Tools, close qFlipper, then open Apps → Tools → Tamagometer Enhanced.",
        "Desktop will select only a verified or remembered Flipper port, check compatibility, and remember it for reconnection."
    ]
    contentItem: ColumnLayout {
        Accessible.role: Accessible.Pane
        Accessible.name: "First-run setup"
        spacing: 16
        Label { text: "FIRST-RUN SETUP · " + (root.viewModel.onboardingStep + 1) + " OF 3"; color: AppTheme.Theme.accent; font.weight: Font.DemiBold }
        Label { Layout.fillWidth: true; text: root.titles[root.viewModel.onboardingStep]; color: AppTheme.Theme.text; font.pixelSize: 24; font.weight: Font.DemiBold; wrapMode: Text.WordWrap }
        Label { Layout.fillWidth: true; text: root.bodies[root.viewModel.onboardingStep]; color: AppTheme.Theme.muted; wrapMode: Text.WordWrap }
        Rectangle {
            Layout.fillWidth: true; implicitHeight: stateLabel.implicitHeight + 24; radius: 10; color: AppTheme.Theme.accentSoft
            Label { id: stateLabel; anchors.fill: parent; anchors.margins: 12; text: root.viewModel.onboardingState; color: AppTheme.Theme.text; wrapMode: Text.WordWrap }
        }
        Item { Layout.fillHeight: true }
        RowLayout {
            Layout.fillWidth: true
            Button { text: "Skip"; onClicked: root.viewModel.skipOnboarding() }
            Item { Layout.fillWidth: true }
            Button { text: "Back"; enabled: root.viewModel.onboardingStep > 0 && !root.viewModel.onboardingReady; onClicked: root.viewModel.onboardingBack() }
            Button {
                text: root.viewModel.onboardingReady ? "Finish setup" : (root.viewModel.onboardingStep === 2 ? "Find Flipper" : "Continue")
                onClicked: root.viewModel.onboardingNext()
            }
        }
    }
}
