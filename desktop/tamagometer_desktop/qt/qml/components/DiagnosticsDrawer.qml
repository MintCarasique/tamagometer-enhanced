import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import "../theme" as AppTheme

Drawer {
    id: root
    required property var viewModel
    edge: Qt.RightEdge
    width: Math.min(parent.width * 0.82, 680)
    height: parent.height
    modal: true
    onClosed: if (viewModel.diagnosticsVisible) viewModel.closeDiagnostics()
    background: Rectangle { color: AppTheme.Theme.surface }
    ColumnLayout {
        Accessible.role: Accessible.Pane
        Accessible.name: "Diagnostics report"
        anchors.fill: parent; anchors.margins: 18; spacing: 12
        RowLayout {
            Layout.fillWidth: true
            Label { Layout.fillWidth: true; text: "Diagnostics"; color: AppTheme.Theme.text; font.pixelSize: 23; font.weight: Font.DemiBold }
            AppButton { iconName: "close"; text: "Close"; onClicked: root.viewModel.closeDiagnostics() }
        }
        Label { Layout.fillWidth: true; text: "The report omits USB hardware IDs and other private identifiers."; color: AppTheme.Theme.muted; wrapMode: Text.WordWrap }
        TextArea {
            Layout.fillWidth: true; Layout.fillHeight: true
            text: root.viewModel.diagnosticsText; readOnly: true; wrapMode: TextEdit.Wrap
            font.family: "Cascadia Mono"; color: AppTheme.Theme.text
            background: Rectangle { color: AppTheme.Theme.surfaceAlt; radius: 10; border.color: AppTheme.Theme.border }
        }
        RowLayout {
            Layout.fillWidth: true
            AppButton { text: "Copy"; onClicked: root.viewModel.copyDiagnostics() }
            AppButton { text: "Export…"; onClicked: exportDialog.open() }
            Item { Layout.fillWidth: true }
        }
    }
    FileDialog {
        id: exportDialog
        title: "Export diagnostic report"
        fileMode: FileDialog.SaveFile
        defaultSuffix: "txt"
        nameFilters: ["Text reports (*.txt)"]
        onAccepted: root.viewModel.exportDiagnostics(selectedFile.toString())
    }
}
