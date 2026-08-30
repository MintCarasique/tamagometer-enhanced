import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

ColumnLayout {
    id: root
    required property var viewModel
    spacing: 12

    ProgressBar {
        id: progress
        objectName: "transferProgress"
        Layout.fillWidth: true
        Layout.preferredHeight: 8
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

    TransferTextSlot {
        objectName: "transferStatusSlot"
        Layout.preferredHeight: 22
        text: root.viewModel.transferStatus
        color: AppTheme.Theme.accent
    }
    AppButton {
        objectName: "primaryTransferAction"
        Layout.fillWidth: true
        primary: true
        iconName: "send"
        text: root.viewModel.primaryActionLabel
        enabled: root.viewModel.canStartTransfer
        onClicked: root.viewModel.startTransfer()
        Accessible.description: root.viewModel.primaryActionHint
    }
    RowLayout {
        objectName: "transferSecondaryActions"
        Layout.fillWidth: true
        Layout.preferredHeight: AppTheme.Theme.controlHeight
        AppButton {
            iconName: "refresh"
            Layout.fillWidth: true
            text: "Repeat"
            enabled: root.viewModel.canRepeatTransfer
            onClicked: root.viewModel.repeatLastTransfer()
        }
        AppButton {
            iconName: "close"
            Layout.fillWidth: true
            text: "Cancel"
            enabled: root.viewModel.canCancelTransfer
            onClicked: root.viewModel.cancelTransfer()
        }
    }
    TransferTextSlot {
        objectName: "transferHintSlot"
        Layout.preferredHeight: 42
        text: root.viewModel.primaryActionHint
        color: AppTheme.Theme.warning
        fontPixelSize: 12
    }
}
