pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Item {
    id: root
    objectName: "catalogGrid"
    required property var catalogModel
    readonly property int scrollbarGutter: 18
    implicitHeight: 440

    GridView {
        id: grid
        anchors.fill: parent
        clip: true
        model: root.catalogModel
        readonly property real usableWidth: width - root.scrollbarGutter
        readonly property int columnCount: Math.max(1, Math.floor(usableWidth / 250))
        cellWidth: Math.max(220, usableWidth / columnCount)
        cellHeight: 88
        currentIndex: root.catalogModel.selectedIndex
        boundsBehavior: Flickable.StopAtBounds
        activeFocusOnTab: true
        keyNavigationEnabled: true
        Accessible.role: Accessible.List
        Accessible.name: "Gift and reward catalog"
        ScrollBar.vertical: AppScrollBar { width: 10 }
        delegate: CatalogItem {
            required property int index
            required property string name
            required property string displayId
            required property string category
            required property string spriteUrl
            required property bool favorite
            width: grid.cellWidth - 10
            height: 78
            rowIndex: index
            itemName: name
            itemDisplayId: displayId
            itemCategory: category
            itemSprite: spriteUrl
            itemFavorite: favorite
            selected: index === grid.currentIndex
            onChosen: { root.catalogModel.select(index); grid.currentIndex = index }
            onFavoriteClicked: root.catalogModel.toggleFavorite(index)
        }
    }

    EmptyState {
        anchors.centerIn: parent
        visible: root.catalogModel.count === 0
        title: "No matching items"
        detail: "Try a different category, name, decimal ID, or hexadecimal ID."
    }
}
