import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

ConnectionCard {
    id: root
    required property var viewModel

    Label {
        text: root.viewModel.pickerTitle
        color: AppTheme.Theme.text
        font.pixelSize: 20
        font.weight: Font.DemiBold
    }
    Label {
        Layout.fillWidth: true
        text: root.viewModel.pickerHint
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
            text: root.viewModel.catalogModel.query
            onTextEdited: root.viewModel.catalogModel.query = text
            Accessible.name: "Search catalog"
        }
        AppComboBox {
            objectName: "categorySelector"
            Layout.preferredWidth: 190
            model: root.viewModel.categories
            onActivated: root.viewModel.catalogModel.category = currentText
            Accessible.name: "Catalog category"
        }
    }
    CatalogGrid {
        Layout.fillWidth: true
        Layout.fillHeight: true
        catalogModel: root.viewModel.catalogModel
    }
}
