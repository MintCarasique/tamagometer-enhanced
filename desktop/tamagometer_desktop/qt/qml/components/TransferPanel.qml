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
    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 130
        radius: 12
        color: AppTheme.Theme.surfaceAlt
        Image {
            anchors.centerIn: parent
            width: 88; height: 88
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
    Label {
        Layout.fillWidth: true
        text: root.viewModel.legacyMode ? "Automatic game or gift" : (root.catalogModel.selectedName || "Select an item")
        color: AppTheme.Theme.text
        font.pixelSize: 17
        font.weight: Font.DemiBold
        wrapMode: Text.WordWrap
    }
    Label {
        visible: !root.viewModel.legacyMode && root.catalogModel.selectedDisplayId.length > 0
        text: root.catalogModel.selectedDisplayId
        color: AppTheme.Theme.muted
    }
    Label {
        Layout.fillWidth: true
        text: root.viewModel.instructions
        color: AppTheme.Theme.muted
        wrapMode: Text.WordWrap
    }
    ProgressBar {
        id: progress
        Layout.fillWidth: true
        value: root.viewModel.transferProgress
        background: Rectangle {
            implicitHeight: 8
            radius: 4
            color: AppTheme.Theme.disabledSurface
            border.color: AppTheme.Theme.border
        }
        contentItem: Item {
            implicitHeight: 8
            Rectangle {
                width: progress.visualPosition * parent.width
                height: parent.height
                radius: 4
                color: AppTheme.Theme.accent
            }
        }
    }
    Label {
        Layout.fillWidth: true
        text: root.viewModel.transferStatus
        color: AppTheme.Theme.accent
        wrapMode: Text.WordWrap
    }
    AppButton {
        objectName: "primaryTransferAction"
        Layout.fillWidth: true
        primary: true
        text: root.viewModel.primaryActionLabel
        enabled: root.viewModel.canStartTransfer
        onClicked: root.viewModel.startTransfer()
        Accessible.description: root.viewModel.primaryActionHint
    }
    RowLayout {
        Layout.fillWidth: true
        AppButton {
            Layout.fillWidth: true
            text: "Repeat"
            enabled: root.viewModel.canRepeatTransfer
            onClicked: root.viewModel.repeatLastTransfer()
        }
        AppButton {
            Layout.fillWidth: true
            text: "Cancel"
            enabled: root.viewModel.canCancelTransfer
            onClicked: root.viewModel.cancelTransfer()
        }
    }
    Label {
        Layout.fillWidth: true
        text: root.viewModel.primaryActionHint
        color: AppTheme.Theme.warning
        wrapMode: Text.WordWrap
        font.pixelSize: 12
    }
}
