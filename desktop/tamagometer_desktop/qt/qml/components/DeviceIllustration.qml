import QtQuick
import "../theme" as AppTheme

Item {
    id: root
    property string device: "tamagotchi"
    property bool back: false
    implicitWidth: device === "flipper" ? 112 : 64
    implicitHeight: 64
    Accessible.role: Accessible.Graphic
    Accessible.name: (device === "flipper" ? "Flipper Zero" : "Tamagotchi")
        + (back ? " rear view" : " front view")

    onDeviceChanged: drawing.requestPaint()
    onBackChanged: drawing.requestPaint()
    Connections {
        target: AppTheme.Theme
        function onDarkChanged() { drawing.requestPaint() }
    }

    Canvas {
        id: drawing
        anchors.fill: parent
        antialiasing: true
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            const logicalWidth = root.device === "flipper" ? 112 : 64
            const scale = Math.min(width / logicalWidth, height / 64)
            if (scale <= 0) return
            ctx.translate((width - logicalWidth * scale) / 2, (height - 64 * scale) / 2)
            ctx.scale(scale, scale)
            ctx.lineWidth = 2
            ctx.lineCap = "round"
            ctx.lineJoin = "round"

            function box(x, y, w, h, radius, fill, stroke) {
                ctx.beginPath()
                ctx.roundedRect(x, y, w, h, radius, radius)
                ctx.fillStyle = fill
                ctx.fill()
                if (stroke) { ctx.strokeStyle = stroke; ctx.stroke() }
            }
            function dot(x, y, radius, fill) {
                ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2)
                ctx.fillStyle = fill; ctx.fill()
            }
            const ink = "#344054"
            const lcd = "#E3EDD1"
            const orange = "#F69B43"
            if (root.device === "flipper") {
                box(3, 12, 106, 40, 12, "#FFFCF7", ink)
                // The IR window is on the nose, opposite the controls.
                box(3, 23, 5, 17, 2, ink, "")
                if (root.back) {
                    box(20, 19, 77, 26, 8, "#F5F1E9", "#D4D0C8")
                    ctx.strokeStyle = orange
                    for (let i = 0; i < 3; ++i) {
                        ctx.beginPath(); ctx.arc(56, 32, 5 + i * 4, 0, Math.PI * 2); ctx.stroke()
                    }
                } else {
                    box(16, 20, 49, 24, 5, "#F6BC77", orange)
                    box(20, 24, 41, 16, 2, lcd, ink)
                    ctx.fillStyle = ink
                    // A small pixel dolphin silhouette, rather than a text label.
                    ctx.beginPath(); ctx.moveTo(28, 33); ctx.lineTo(34, 29)
                    ctx.lineTo(40, 29); ctx.lineTo(44, 26); ctx.lineTo(44, 30)
                    ctx.lineTo(51, 32); ctx.lineTo(45, 33); ctx.lineTo(41, 36)
                    ctx.lineTo(38, 33); ctx.lineTo(32, 33); ctx.lineTo(27, 37)
                    ctx.closePath(); ctx.fill()
                    dot(45, 31, 0.8, lcd)
                    box(76, 22, 23, 21, 7, orange, "#CB752B")
                    ctx.fillStyle = "#FFFCF7"
                    ctx.fillRect(85, 25, 5, 15); ctx.fillRect(80, 30, 15, 5)
                    dot(69, 38, 2.5, orange)
                }
            } else {
                // A tapered egg shell with a recessed display and three buttons.
                ctx.beginPath(); ctx.moveTo(32, 4)
                ctx.bezierCurveTo(44, 4, 57, 26, 57, 40)
                ctx.bezierCurveTo(57, 54, 47, 60, 32, 60)
                ctx.bezierCurveTo(17, 60, 7, 54, 7, 40)
                ctx.bezierCurveTo(7, 26, 20, 4, 32, 4)
                ctx.closePath(); ctx.fillStyle = AppTheme.Theme.accentSoft
                ctx.fill(); ctx.strokeStyle = AppTheme.Theme.accent; ctx.stroke()
                box(27, 3, 10, 5, 2, ink, "")
                if (root.back) {
                    box(19, 23, 26, 28, 8, AppTheme.Theme.surface, AppTheme.Theme.accent)
                    dot(32, 29, 1.4, AppTheme.Theme.accent)
                    ctx.strokeStyle = AppTheme.Theme.accent
                    ctx.beginPath(); ctx.arc(32, 40, 6, 0, Math.PI * 2); ctx.stroke()
                } else {
                    box(15, 22, 34, 25, 8, AppTheme.Theme.surface, AppTheme.Theme.accent)
                    box(20, 27, 24, 15, 3, lcd, ink)
                    ctx.fillStyle = ink
                    ctx.fillRect(25, 31, 3, 3); ctx.fillRect(36, 31, 3, 3)
                    ctx.fillRect(29, 36, 6, 2)
                    for (let i = 0; i < 3; ++i) dot(22 + i * 10, 52, 2.6, AppTheme.Theme.accent)
                    // Small shell highlights give depth without making the icon busy.
                    ctx.strokeStyle = AppTheme.Theme.surface
                    ctx.beginPath(); ctx.moveTo(18, 18); ctx.lineTo(22, 12); ctx.stroke()
                }
            }
        }
    }
}
