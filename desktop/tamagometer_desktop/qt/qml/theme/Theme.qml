pragma Singleton
import QtQuick

QtObject {
    property bool dark: false
    readonly property color background: dark ? "#0B1020" : "#F3F5FA"
    readonly property color surface: dark ? "#151B2B" : "#FFFFFF"
    readonly property color surfaceAlt: dark ? "#1D2435" : "#F9FAFB"
    readonly property color text: dark ? "#F2F4F7" : "#182230"
    readonly property color muted: dark ? "#98A2B3" : "#667085"
    readonly property color accent: dark ? "#9B8CFF" : "#6757D9"
    readonly property color accentSoft: dark ? "#29234A" : "#EEEAFE"
    readonly property color border: dark ? "#344054" : "#E3E7EF"
    readonly property color success: dark ? "#75E0A7" : "#067647"
    readonly property color warning: dark ? "#FEC84B" : "#B54708"
}
