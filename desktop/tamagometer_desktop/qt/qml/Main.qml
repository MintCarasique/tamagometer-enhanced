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

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: window.compactLayout ? 150 : 112
                color: AppTheme.Theme.accent
                ColumnLayout {
                    anchors.fill: parent
                    anchors.topMargin: 14; anchors.bottomMargin: 14
                    anchors.leftMargin: 28; anchors.rightMargin: 28
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            Layout.fillWidth: true
                            text: "Tamagometer Enhanced\n<span style='font-size:12px'>Desktop " + window.viewModel.version + " · PySide6/QML preview</span>"
                            textFormat: Text.RichText; color: "white"; font.pixelSize: window.compactLayout ? 20 : 24; font.weight: Font.DemiBold
                        }
                        StatusBadge { text: window.viewModel.connectionStatus; Accessible.name: "Connection status: " + text }
                    }
                    Flow {
                        Layout.fillWidth: true; spacing: 8
                        AppButton { objectName: "headerDiagnosticsButton"; iconName: "diagnostics"; text: "Diagnostics"; onClicked: window.viewModel.openDiagnostics(); Accessible.name: "Open diagnostics, Control D" }
                        AppButton { objectName: "headerSettingsButton"; iconName: "settings"; text: "Settings"; onClicked: window.viewModel.openSettings(); Accessible.name: "Open settings, Control comma" }
                        AppButton {
                            objectName: "headerThemeButton"
                            iconName: window.viewModel.darkTheme ? "sun" : "moon"
                            text: window.viewModel.darkTheme ? "Light" : "Dark"
                            onClicked: window.viewModel.toggleTheme()
                            Accessible.name: "Toggle color theme"
                        }
                    }
                }
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
                ConnectionCard {
                    Layout.fillWidth: true
                    RowLayout {
                        Layout.fillWidth: true
                        AppComboBox {
                            objectName: "portSelector"
                            Layout.fillWidth: true
                            model: window.viewModel.ports
                            textRole: "label"
                            valueRole: "device"
                            currentIndex: window.viewModel.selectedPortIndex
                            enabled: window.viewModel.connectionState !== "connecting" && !window.viewModel.canCancelTransfer
                            onActivated: window.viewModel.setSelectedPort(currentValue)
                            Accessible.name: "Flipper serial port"
                        }
                        AppButton { objectName: "portRefreshButton"; iconName: "refresh"; text: "Refresh"; onClicked: window.viewModel.refreshPorts() }
                        AppButton {
                            iconName: "link"
                            text: window.viewModel.connected ? "Disconnect" : (window.viewModel.connectionState === "connecting" ? "Connecting…" : "Connect")
                            enabled: window.viewModel.connectionState !== "connecting" && !window.viewModel.canCancelTransfer
                            onClicked: window.viewModel.toggleConnection()
                            Accessible.name: text + " Flipper"
                        }
                    }
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

                    ConnectionCard {
                        objectName: "catalogCard"
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.preferredWidth: 700
                        Layout.minimumHeight: window.viewModel.legacyMode ? 260 : 620
                        visible: !window.viewModel.legacyMode

                        Label {
                            text: window.viewModel.pickerTitle
                            color: AppTheme.Theme.text
                            font.pixelSize: 20
                            font.weight: Font.DemiBold
                        }
                        Label {
                            Layout.fillWidth: true
                            text: window.viewModel.pickerHint
                            color: AppTheme.Theme.muted
                            wrapMode: Text.WordWrap
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            TextField {
                                objectName: "catalogSearch"
                                Layout.fillWidth: true
                                implicitHeight: AppTheme.Theme.controlHeight
                                placeholderText: "Search name, category, decimal or hex ID"
                                text: window.viewModel.catalogModel.query
                                onTextEdited: window.viewModel.catalogModel.query = text
                                Accessible.name: "Search catalog"
                            }
                            AppComboBox {
                                objectName: "categorySelector"
                                Layout.preferredWidth: 190
                                model: window.viewModel.categories
                                onActivated: window.viewModel.catalogModel.category = currentText
                                Accessible.name: "Catalog category"
                            }
                        }
                        CatalogGrid {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            catalogModel: window.viewModel.catalogModel
                        }
                    }

                    ConnectionCard {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 700
                        Layout.minimumHeight: 260
                        visible: window.viewModel.legacyMode
                        Label {
                            text: "Original Connection fallback"
                            color: AppTheme.Theme.text
                            font.pixelSize: 20
                            font.weight: Font.DemiBold
                        }
                        Label {
                            Layout.fillWidth: true
                            text: "There is no selectable catalog in this mode. The Tamagotchi randomly chooses a game or gift after the fallback starts."
                            color: AppTheme.Theme.muted
                            wrapMode: Text.WordWrap
                        }
                        Label {
                            Layout.fillWidth: true
                            text: window.viewModel.instructions
                            color: AppTheme.Theme.text
                            wrapMode: Text.WordWrap
                        }
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
