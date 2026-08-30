import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

ConnectionCard {
    id: root
    required property var viewModel
    required property var catalogModel

    Label {
        text: "Transfer"
        color: AppTheme.Theme.text
        font.pixelSize: 19
        font.weight: Font.DemiBold
    }
    TransferSummary {
        Layout.fillWidth: true
        viewModel: root.viewModel
        catalogModel: root.catalogModel
    }
    Item { Layout.fillHeight: true }
    TransferActions {
        Layout.fillWidth: true
        viewModel: root.viewModel
    }
}
