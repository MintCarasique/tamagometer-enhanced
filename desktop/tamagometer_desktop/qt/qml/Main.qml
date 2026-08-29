import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "theme" as AppTheme

ApplicationWindow {
    id: window
    // Context properties are supplied by QQmlApplicationEngine at startup.
    // qmllint disable unqualified
    property var viewModel: appViewModel
    // qmllint enable unqualified
    width: 1120
    height: 800
    minimumWidth: 720
    minimumHeight: 620
    visible: true
    title: "Tamagometer Enhanced " + window.viewModel.version
    color: AppTheme.Theme.background

    Binding { target: AppTheme.Theme; property: "dark"; value: window.viewModel.darkTheme }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            width: parent.width
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 104
                color: AppTheme.Theme.accent
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 28; anchors.rightMargin: 28
                    Label {
                        Layout.fillWidth: true
                        text: "Tamagometer Enhanced\n<span style='font-size:12px'>Desktop " + window.viewModel.version + " · PySide6/QML preview</span>"
                        textFormat: Text.RichText
                        color: "white"
                        font.pixelSize: 24
                        font.weight: Font.DemiBold
                    }
                    StatusBadge { text: window.viewModel.connectionStatus }
                    Button {
                        text: window.viewModel.darkTheme ? "☀ Light" : "☾ Dark"
                        onClicked: window.viewModel.toggleTheme()
                        Accessible.name: "Toggle color theme"
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 24; Layout.rightMargin: 24
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
                        ComboBox {
                            Layout.fillWidth: true
                            model: window.viewModel.ports
                            textRole: "label"
                            valueRole: "device"
                            currentIndex: window.viewModel.selectedPortIndex
                            enabled: window.viewModel.connectionState !== "connecting" && !window.viewModel.canCancelTransfer
                            onActivated: window.viewModel.setSelectedPort(currentValue)
                            Accessible.name: "Flipper serial port"
                        }
                        Button { text: "Refresh"; onClicked: window.viewModel.refreshPorts() }
                        Button {
                            text: window.viewModel.connected ? "Disconnect" : (window.viewModel.connectionState === "connecting" ? "Connecting…" : "Connect")
                            enabled: window.viewModel.connectionState !== "connecting" && !window.viewModel.canCancelTransfer
                            onClicked: window.viewModel.toggleConnection()
                        }
                    }
                }
                InlineNotice {
                    Layout.fillWidth: true
                    visible: window.viewModel.noticeSummary.length > 0
                    text: window.viewModel.noticeSummary
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: window.width >= 980 ? 2 : 1
                    columnSpacing: 16
                    rowSpacing: 16

                    ConnectionCard {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 700
                        Layout.minimumHeight: window.viewModel.legacyMode ? 260 : 610
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
                                Layout.fillWidth: true
                                placeholderText: "Search name, category, decimal or hex ID"
                                text: window.viewModel.catalogModel.query
                                onTextEdited: window.viewModel.catalogModel.query = text
                                Accessible.name: "Search catalog"
                            }
                            ComboBox {
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
                        Layout.fillWidth: true
                        Layout.preferredWidth: 340
                        Layout.alignment: Qt.AlignTop
                        viewModel: window.viewModel
                        catalogModel: window.viewModel.catalogModel
                    }
                }
            }
        }
    }
}
