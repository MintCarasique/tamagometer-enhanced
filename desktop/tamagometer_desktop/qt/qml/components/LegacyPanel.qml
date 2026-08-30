import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as AppTheme

ConnectionCard {
    id: root
    required property var viewModel

    Label {
        text: "Original Connection fallback"
        color: AppTheme.Theme.text
        font.pixelSize: 20
        font.weight: Font.DemiBold
    }
    Label {
        Layout.fillWidth: true
        text: "There is no selectable catalog in this mode. The Tamagotchi "
            + "randomly chooses a game or gift after the fallback starts."
        color: AppTheme.Theme.muted
        wrapMode: Text.WordWrap
    }
    Label {
        Layout.fillWidth: true
        text: root.viewModel.instructions
        color: AppTheme.Theme.text
        wrapMode: Text.WordWrap
    }
}
