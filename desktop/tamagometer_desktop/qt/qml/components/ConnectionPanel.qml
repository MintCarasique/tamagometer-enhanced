import QtQuick
import QtQuick.Layouts

ConnectionCard {
    id: root
    required property var viewModel

    RowLayout {
        Layout.fillWidth: true
        AppComboBox {
            objectName: "portSelector"
            Layout.fillWidth: true
            model: root.viewModel.ports
            textRole: "label"
            valueRole: "device"
            currentIndex: root.viewModel.selectedPortIndex
            enabled: root.viewModel.connectionState !== "connecting"
                && !root.viewModel.canCancelTransfer
            onActivated: root.viewModel.setSelectedPort(currentValue)
            Accessible.name: "Flipper serial port"
        }
        AppButton {
            objectName: "portRefreshButton"
            iconName: "refresh"
            text: "Refresh"
            onClicked: root.viewModel.refreshPorts()
        }
        AppButton {
            iconName: "link"
            text: root.viewModel.connected
                ? "Disconnect"
                : (root.viewModel.connectionState === "connecting" ? "Connecting…" : "Connect")
            enabled: root.viewModel.connectionState !== "connecting"
                && !root.viewModel.canCancelTransfer
            onClicked: root.viewModel.toggleConnection()
            Accessible.name: text + " Flipper"
        }
    }
}
