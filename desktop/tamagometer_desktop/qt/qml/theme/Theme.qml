pragma Singleton
import QtQuick

QtObject {
    property bool dark: false
    property bool reducedMotion: false
    readonly property color background: dark ? "#0B1020" : "#F3F5FA"
    readonly property color surface: dark ? "#151B2B" : "#FFFFFF"
    readonly property color surfaceAlt: dark ? "#1D2435" : "#F9FAFB"
    readonly property color control: dark ? "#252D40" : "#FFFFFF"
    readonly property color controlHover: dark ? "#303A50" : "#F4F1FF"
    readonly property color disabledSurface: dark ? "#202738" : "#F2F4F7"
    readonly property color text: dark ? "#F2F4F7" : "#182230"
    readonly property color muted: dark ? "#98A2B3" : "#667085"
    readonly property color disabledText: dark ? "#AAB2C0" : "#667085"
    readonly property color accent: dark ? "#9B8CFF" : "#6757D9"
    readonly property color accentSoft: dark ? "#29234A" : "#EEEAFE"
    readonly property color border: dark ? "#344054" : "#E3E7EF"
    readonly property color borderStrong: dark ? "#667085" : "#98A2B3"
    readonly property color success: dark ? "#75E0A7" : "#067647"
    readonly property color warning: dark ? "#FEC84B" : "#B54708"
}
