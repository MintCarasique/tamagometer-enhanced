import QtQuick

Item {
    id: root
    property string name: ""
    property color color: "#000000"
    property bool filled: false
    implicitWidth: 18
    implicitHeight: 18

    onNameChanged: canvas.requestPaint()
    onColorChanged: canvas.requestPaint()
    onFilledChanged: canvas.requestPaint()

    Canvas {
        id: canvas
        anchors.fill: parent
        antialiasing: true
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()

        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            const scale = Math.min(width, height) / 24
            ctx.scale(scale, scale)
            ctx.translate((width / scale - 24) / 2, (height / scale - 24) / 2)
            ctx.strokeStyle = root.color
            ctx.fillStyle = root.color
            ctx.lineWidth = 1.9
            ctx.lineCap = "round"
            ctx.lineJoin = "round"

            if (root.name === "chevron-down") {
                ctx.beginPath(); ctx.moveTo(6, 9); ctx.lineTo(12, 15); ctx.lineTo(18, 9); ctx.stroke()
            } else if (root.name === "star") {
                ctx.beginPath()
                for (let i = 0; i < 10; ++i) {
                    const angle = -Math.PI / 2 + i * Math.PI / 5
                    const radius = i % 2 === 0 ? 8.5 : 3.8
                    const x = 12 + Math.cos(angle) * radius
                    const y = 12 + Math.sin(angle) * radius
                    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y)
                }
                ctx.closePath(); if (root.filled) ctx.fill(); else ctx.stroke()
            } else if (root.name === "sun") {
                ctx.beginPath(); ctx.arc(12, 12, 3.6, 0, Math.PI * 2); ctx.stroke()
                for (let i = 0; i < 8; ++i) {
                    const angle = i * Math.PI / 4
                    ctx.beginPath()
                    ctx.moveTo(12 + Math.cos(angle) * 6.5, 12 + Math.sin(angle) * 6.5)
                    ctx.lineTo(12 + Math.cos(angle) * 9, 12 + Math.sin(angle) * 9)
                    ctx.stroke()
                }
            } else if (root.name === "moon") {
                ctx.beginPath(); ctx.moveTo(15.8, 4.8)
                ctx.bezierCurveTo(10.2, 5.5, 7.2, 11.8, 10.4, 16.4)
                ctx.bezierCurveTo(12.3, 19.2, 16.2, 19.8, 19.1, 17.6)
                ctx.bezierCurveTo(17.4, 20.1, 13.8, 21.2, 10.6, 19.8)
                ctx.bezierCurveTo(5.9, 17.8, 4.2, 12.1, 6.5, 7.7)
                ctx.bezierCurveTo(8.3, 4.4, 12.2, 2.9, 15.8, 4.8); ctx.stroke()
            } else if (root.name === "settings") {
                ctx.beginPath(); ctx.arc(12, 12, 3.2, 0, Math.PI * 2); ctx.stroke()
                for (let i = 0; i < 8; ++i) {
                    const angle = i * Math.PI / 4
                    ctx.beginPath()
                    ctx.moveTo(12 + Math.cos(angle) * 6, 12 + Math.sin(angle) * 6)
                    ctx.lineTo(12 + Math.cos(angle) * 9, 12 + Math.sin(angle) * 9)
                    ctx.stroke()
                }
            } else if (root.name === "diagnostics") {
                ctx.strokeRect(4.5, 3.5, 15, 17)
                ctx.beginPath(); ctx.moveTo(7, 14); ctx.lineTo(9.5, 11); ctx.lineTo(12, 15); ctx.lineTo(15, 8); ctx.lineTo(17, 10); ctx.stroke()
            } else if (root.name === "refresh") {
                ctx.beginPath(); ctx.arc(12, 12, 7, -0.55, 4.25); ctx.stroke()
                ctx.beginPath(); ctx.moveTo(5.2, 5.8); ctx.lineTo(5.8, 10); ctx.lineTo(9.5, 7.8); ctx.stroke()
            } else if (root.name === "link") {
                ctx.beginPath(); ctx.arc(8, 12, 4.5, 0.75, 5.5); ctx.stroke()
                ctx.beginPath(); ctx.arc(16, 12, 4.5, 3.9, 8.65); ctx.stroke()
                ctx.beginPath(); ctx.moveTo(9.5, 12); ctx.lineTo(14.5, 12); ctx.stroke()
            } else if (root.name === "send") {
                ctx.beginPath(); ctx.moveTo(3.5, 5); ctx.lineTo(20.5, 12); ctx.lineTo(3.5, 19); ctx.lineTo(7, 12); ctx.closePath(); ctx.stroke()
                ctx.beginPath(); ctx.moveTo(7, 12); ctx.lineTo(15, 12); ctx.stroke()
            } else if (root.name === "close") {
                ctx.beginPath(); ctx.moveTo(6, 6); ctx.lineTo(18, 18); ctx.moveTo(18, 6); ctx.lineTo(6, 18); ctx.stroke()
            }
        }
    }
}
