import QtQuick
import QtQuick.Controls
import "../theme" as AppTheme

Rectangle {
    id: card
    required property int rowIndex
    required property string itemName
    required property string itemDisplayId
    required property string itemCategory
    required property string itemSprite
    required property bool itemFavorite
    property bool selected: false
    signal chosen(int index)
    signal favoriteClicked(int index)
    activeFocusOnTab: true
    Accessible.role: Accessible.ListItem
    Accessible.name: card.itemName + ", " + card.itemDisplayId
    Accessible.description: card.itemCategory + (card.itemFavorite ? ", favorite" : "")
    Keys.onReturnPressed: card.chosen(card.rowIndex)
    Keys.onEnterPressed: card.chosen(card.rowIndex)
    Keys.onSpacePressed: card.chosen(card.rowIndex)
    Keys.onPressed: event => {
        if (event.key === Qt.Key_F) { card.favoriteClicked(card.rowIndex); event.accepted = true }
    }

    radius: 12
    color: selected ? AppTheme.Theme.accentSoft : AppTheme.Theme.surfaceAlt
    border.width: selected || activeFocus ? 2 : 1
    border.color: selected || activeFocus ? AppTheme.Theme.accent : AppTheme.Theme.border

    MouseArea {
        anchors.fill: parent
        onClicked: card.chosen(card.rowIndex)
        onPressed: card.forceActiveFocus()
    }
    Image {
        id: sprite
        x: 12; y: 14; width: 50; height: 50
        source: card.itemSprite
        fillMode: Image.PreserveAspectFit
        visible: source.toString().length > 0
        smooth: false
    }
    Label {
        x: 74; y: 12
        width: parent.width - 118
        text: card.itemName
        color: AppTheme.Theme.text
        elide: Text.ElideRight
        font.weight: Font.DemiBold
    }
    Label {
        x: 74; y: 38
        width: parent.width - 86
        text: card.itemDisplayId + "  ·  " + card.itemCategory
        color: AppTheme.Theme.muted
        elide: Text.ElideRight
        font.pixelSize: 12
    }
    ToolButton {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 6
        text: card.itemFavorite ? "★" : "☆"
        onClicked: card.favoriteClicked(card.rowIndex)
        Accessible.name: card.itemFavorite ? "Remove from favorites" : "Add to favorites"
        Accessible.description: "Favorite control for " + card.itemName
    }
}
