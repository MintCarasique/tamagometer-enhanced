import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "dialogs"
import "theme" as AppTheme

ApplicationWindow {
    id: window
    objectName: "mainWindow"
    // Context properties are supplied by QQmlApplicationEngine at startup.
    // qmllint disable unqualified
    property var viewModel: appViewModel
    // qmllint enable unqualified
    width: 1280
    height: 940
    minimumWidth: 720
    minimumHeight: 620
    visible: true
    title: "Tamagometer Enhanced " + window.viewModel.version
    color: AppTheme.Theme.background
    palette.window: AppTheme.Theme.background
    palette.windowText: AppTheme.Theme.text
    palette.base: AppTheme.Theme.surfaceAlt
    palette.alternateBase: AppTheme.Theme.surface
    palette.text: AppTheme.Theme.text
    palette.button: AppTheme.Theme.control
    palette.buttonText: AppTheme.Theme.text
    palette.highlight: AppTheme.Theme.accent
    palette.highlightedText: "#FFFFFF"
    palette.placeholderText: AppTheme.Theme.muted
    palette.toolTipBase: AppTheme.Theme.surface
    palette.toolTipText: AppTheme.Theme.text
    palette.link: AppTheme.Theme.accent
    palette.disabled.button: AppTheme.Theme.disabledSurface
    palette.disabled.buttonText: AppTheme.Theme.disabledText
    palette.disabled.text: AppTheme.Theme.disabledText
    readonly property string layoutClass: width < 820 ? "compact" : (width < 1180 ? "medium" : "wide")
    readonly property bool compactLayout: layoutClass === "compact"

    Binding { target: AppTheme.Theme; property: "dark"; value: window.viewModel.darkTheme }
    Binding { target: AppTheme.Theme; property: "reducedMotion"; value: window.viewModel.reducedMotion }
    Shortcut { sequence: "Ctrl+,"; onActivated: window.viewModel.openSettings() }
    Shortcut { sequence: "Ctrl+D"; onActivated: window.viewModel.openDiagnostics() }
    Shortcut { sequence: "Ctrl+R"; enabled: window.viewModel.canRepeatTransfer; onActivated: window.viewModel.repeatLastTransfer() }
    Shortcut { sequence: "Escape"; enabled: window.viewModel.canCancelTransfer; onActivated: window.viewModel.cancelTransfer() }

    ScrollView {
        objectName: "mainScrollView"
        anchors.fill: parent
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical: AppScrollBar { objectName: "mainVerticalScrollBar" }

        ColumnLayout {
            width: parent.width
            height: Math.max(implicitHeight, window.height)
            spacing: 0

            AppHeader {
                Layout.fillWidth: true
                viewModel: window.viewModel
                compact: window.compactLayout
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.leftMargin: window.compactLayout ? 12 : 24
                Layout.rightMargin: window.compactLayout ? 12 : 24
                Layout.topMargin: 18; Layout.bottomMargin: 26
                spacing: 14

                DeviceModeTabs {
                    Layout.fillWidth: true
                    modes: window.viewModel.modes
                    currentMode: window.viewModel.modeKey
                    onModeSelected: key => window.viewModel.setMode(key)
                }
                ConnectionPanel {
                    Layout.fillWidth: true
                    viewModel: window.viewModel
                }
                InlineNotice {
                    Layout.fillWidth: true
                    visible: window.viewModel.noticeSummary.length > 0
                    text: window.viewModel.noticeSummary
                }
                AppButton {
                    iconName: "diagnostics"
                    visible: window.viewModel.noticeDetail.length > 0
                    text: "Show technical details"
                    onClicked: window.viewModel.openDiagnostics()
                }

                GridLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    columns: window.compactLayout ? 1 : 2
                    columnSpacing: 16
                    rowSpacing: 16

                    CatalogPanel {
                        objectName: "catalogCard"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.preferredWidth: 700
                        Layout.minimumHeight: window.viewModel.legacyMode ? 260 : 620
                        visible: !window.viewModel.legacyMode
                        viewModel: window.viewModel
                    }

                    LegacyPanel {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 700
                        Layout.minimumHeight: 260
                        visible: window.viewModel.legacyMode
                        viewModel: window.viewModel
                    }

                    TransferPanel {
                        objectName: "transferPanel"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.preferredWidth: 340
                        Layout.alignment: Qt.AlignTop
                        viewModel: window.viewModel
                        catalogModel: window.viewModel.catalogModel
                    }
                }
            }
        }
    }

    OnboardingDialog {
        id: onboarding
        viewModel: window.viewModel
        visible: window.viewModel.onboardingVisible
    }
    SettingsDialog {
        id: settingsDialog
        viewModel: window.viewModel
        visible: window.viewModel.settingsVisible
    }
    DiagnosticsDrawer {
        id: diagnostics
        viewModel: window.viewModel
        visible: window.viewModel.diagnosticsVisible
    }
}
