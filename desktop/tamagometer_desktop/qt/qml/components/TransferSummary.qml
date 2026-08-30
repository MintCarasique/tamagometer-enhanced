import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

ColumnLayout {
    id: root
    required property var viewModel
    required property var catalogModel
    spacing: 12

    Rectangle {
        objectName: "transferPreview"
        Layout.fillWidth: true
        Layout.preferredHeight: 130
        radius: 12
        color: AppTheme.Theme.surfaceAlt
        Image {
            anchors.centerIn: parent
            width: 88
            height: 88
            source: root.catalogModel.selectedSpriteUrl
            fillMode: Image.PreserveAspectFit
            smooth: false
            visible: !root.viewModel.legacyMode && source.toString().length > 0
        }
        Label {
            anchors.centerIn: parent
            visible: root.viewModel.legacyMode || root.catalogModel.selectedSpriteUrl.length === 0
            text: root.viewModel.legacyMode ? "IR ↔ Flipper" : "No preview"
            color: AppTheme.Theme.muted
            font.pixelSize: 17
        }
    }

    TransferTextSlot {
        objectName: "transferTitleSlot"
        Layout.preferredHeight: 52
        text: root.viewModel.legacyMode
            ? "Automatic game or gift"
            : (root.catalogModel.selectedName || "Select an item")
        color: AppTheme.Theme.text
        fontPixelSize: 17
        fontWeight: Font.DemiBold
    }
    TransferTextSlot {
        objectName: "transferMetadataSlot"
        Layout.preferredHeight: 22
        text: root.viewModel.legacyMode ? "" : root.catalogModel.selectedDisplayId
        color: AppTheme.Theme.muted
    }
    TransferTextSlot {
        objectName: "transferInstructionsSlot"
        Layout.preferredHeight: 76
        text: root.viewModel.instructions
        color: AppTheme.Theme.muted
    }
}
