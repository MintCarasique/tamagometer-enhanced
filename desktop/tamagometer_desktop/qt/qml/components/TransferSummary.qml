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
        readonly property bool hasSprite: !root.viewModel.legacyMode
            && root.catalogModel.selectedSpriteUrl.length > 0
        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 6
            width: 76
            height: 76
            source: root.catalogModel.selectedSpriteUrl
            fillMode: Image.PreserveAspectFit
            smooth: false
            visible: parent.hasSprite
        }
        DeviceGuide {
            objectName: "transferDeviceGuide"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 6
            width: parent.width - 16
            height: implicitHeight
            compact: parent.hasSprite
            friends: root.viewModel.modeKey === "friends"
            active: root.viewModel.canCancelTransfer
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
