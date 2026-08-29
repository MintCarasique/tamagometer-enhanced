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
        Layout.fillWidth: true
        value: 0
    }
    Button {
        Layout.fillWidth: true
        text: root.viewModel.primaryActionLabel
        enabled: false
        Accessible.description: root.viewModel.primaryActionHint
    }
    Label {
        Layout.fillWidth: true
        text: root.viewModel.primaryActionHint
        color: AppTheme.Theme.warning
        wrapMode: Text.WordWrap
        font.pixelSize: 12
    }
}
