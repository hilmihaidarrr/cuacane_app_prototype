import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtCharts 2.15
import AppTheme 1.0


Item {
    id: root
    width: 1920
    height: 1080

    property real angle: 0
    property var directionText: "-"
    property var speedText: "-"
    property var chartModel: []
    property bool showLabels: false
    property string bufferStatusText: "⏳ Buffer not Enough"
    property var dirChartModel: []
    property var speedChartModel: []
    property var chart1hDirModel: []
    property var chart1hSpeedModel: []
    property var chart3hDirModel: []
    property var chart3hSpeedModel: []
    property var chart6hDirModel: []
    property var chart6hSpeedModel: []
    property bool showDirLabels: false
    property bool showSpeedLabels: false
    property bool show1hLabels: false
    property bool show3hLabels: false
    property bool show6hLabels: false


    Timer {
        id: labelDrawTimer
        interval: 500
        repeat: false
        onTriggered: {
            showLabels = false
            Qt.callLater(() => {
                showLabels = true
                console.log("[DEBUG] Labels will now render")
            })
        }
    }

    function getCardinalDirection(deg) {
        if (deg >= 337.5 || deg < 22.5) return "N"
        else if (deg < 67.5) return "NE"
        else if (deg < 112.5) return "E"
        else if (deg < 157.5) return "SE"
        else if (deg < 202.5) return "S"
        else if (deg < 247.5) return "SW"
        else if (deg < 292.5) return "W"
        else return "NW"
    }

    Connections {
        target: windPredictionModel
        function onPredictionChanged() {
            let deg = windPredictionModel.predictionDirection
            let rot = (deg + 180) % 360
            angleAnim.from = root.angle
            angleAnim.to = rot
            angleAnim.start()
            root.angle = rot

            directionText = deg.toFixed(1) + "° (" + getCardinalDirection(deg) + ")"
            speedText = windPredictionModel.predictionSpeed.toFixed(2) + " m/s"
            bufferStatusText = windPredictionModel.bufferReady ? "✅ Ready for Prediction" : "⏳ Buffer not Ready"

            // Bersihkan semua series
            series15mDir.clear();  series15mSpeed.clear()
            series1hDir.clear();   series1hSpeed.clear()
            series3hDir.clear();   series3hSpeed.clear()
            series6hDir.clear();   series6hSpeed.clear()

            // Model Chart per horizon
            dirChartModel = []
            speedChartModel = []
            chart1hDirModel = []
            chart1hSpeedModel = []
            chart3hDirModel = []
            chart3hSpeedModel = []
            chart6hDirModel = []
            chart6hSpeedModel = []

            // === 15m ===
            for (let i = 0; i < windPredictionModel.chart15m.length; i++) {
                let d = windPredictionModel.chart15m[i]
                series15mDir.append(i, d.dir)
                series15mSpeed.append(i, d.speed)
                dirChartModel.push({ index: i, value: d.dir, timestamp: d.timestamp })
                speedChartModel.push({ index: i, value: d.speed, timestamp: d.timestamp })
            }

            // === 1h ===
            for (let i = 0; i < windPredictionModel.chart1h.length; i++) {
                let d = windPredictionModel.chart1h[i]
                series1hDir.append(i, d.dir)
                series1hSpeed.append(i, d.speed)
                chart1hDirModel.push({ index: i, value: d.dir, timestamp: d.timestamp })
                chart1hSpeedModel.push({ index: i, value: d.speed, timestamp: d.timestamp })
            }

            // === 3h ===
            for (let i = 0; i < windPredictionModel.chart3h.length; i++) {
                let d = windPredictionModel.chart3h[i]
                series3hDir.append(i, d.dir)
                series3hSpeed.append(i, d.speed)
                chart3hDirModel.push({ index: i, value: d.dir, timestamp: d.timestamp })
                chart3hSpeedModel.push({ index: i, value: d.speed, timestamp: d.timestamp })
            }

            // === 6h ===
            for (let i = 0; i < windPredictionModel.chart6h.length; i++) {
                let d = windPredictionModel.chart6h[i]
                series6hDir.append(i, d.dir)
                series6hSpeed.append(i, d.speed)
                chart6hDirModel.push({ index: i, value: d.dir, timestamp: d.timestamp })
                chart6hSpeedModel.push({ index: i, value: d.speed, timestamp: d.timestamp })
            }

            // Tampilkan label setelah update
            showDirLabels = false
            showSpeedLabels = false
            show1hLabels = false
            show3hLabels = false
            show6hLabels = false
            Qt.callLater(() => {
                showDirLabels = true
                showSpeedLabels = true
                show1hLabels = true
                show3hLabels = true
                show6hLabels = true
            })

            console.log("[✅] Prediksi dan grafik diperbarui")
        }
    }

    Rectangle {
        anchors.fill: parent
        color: settingsManager.darkMode ? Theme.darkBackground : Theme.lightBackground

        ColumnLayout {
            anchors.fill: parent
            spacing: 20
            anchors.margins: 24

            Text {
                text: "📊 Wind Direction and Speed Prediction"
                font.pixelSize: 32
                font.bold: true
                color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                Layout.alignment: Qt.AlignHCenter
            }

            RowLayout {
                spacing: 24
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    spacing: 20
                    Layout.preferredWidth: 600
                    Layout.fillHeight: true

                    Rectangle {
                        width: 300
                        height: 300
                        radius: 150
                        color: settingsManager.darkMode ? Theme.darkCard : Theme.lightCard
                        border.color: settingsManager.darkMode ? Theme.borderDark : Theme.borderLight
                        border.width: 2
                        Layout.alignment: Qt.AlignHCenter

                        // === JARUM ===
                        Rectangle {
                            id: needle
                            width: 4
                            height: 130
                            radius: 2
                            color: "red"
                            anchors.centerIn: parent
                            anchors.verticalCenterOffset: -65
                            transformOrigin: Item.Bottom
                            rotation: root.angle
                        }

                        // === LABEL ARAH ===
                        Repeater {
                            model: [
                                { label: "N", angle: 0 },
                                { label: "NE", angle: 45 },
                                { label: "E", angle: 90 },
                                { label: "SE", angle: 135 },
                                { label: "S", angle: 180 },
                                { label: "SW", angle: 225 },
                                { label: "W", angle: 270 },
                                { label: "NW", angle: 315 }
                            ]
                            delegate: Text {
                                text: modelData.label
                                font.pixelSize: 14
                                font.bold: true
                                color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                                anchors.centerIn: undefined
                                x: parent.width / 2 + 130 * Math.sin(Math.PI * modelData.angle / 180) - width / 2
                                y: parent.height / 2 - 130 * Math.cos(Math.PI * modelData.angle / 180) - height / 2
                            }
                        }
                    }

                    Text {
                        text: windPredictionModel.predictionExpiry
                        font.pixelSize: 16
                        color: windPredictionModel.predictionExpiry.startsWith("❌") ? "red" : "gray"
                        horizontalAlignment: Text.AlignHCenter
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Rectangle {
                        width: 400
                        height: 100
                        radius: 12
                        color: settingsManager.darkMode ? Theme.darkCard : Theme.lightCard
                        border.color: settingsManager.darkMode ? Theme.borderDark : Theme.borderLight
                        border.width: 1
                        Layout.alignment: Qt.AlignHCenter

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 24

                            Column {
                                spacing: 4
                                Text { text: "Wind Direction (From)"; font.pixelSize: 18; color: settingsManager.darkMode ? Theme.darkText : Theme.lightText }
                                Text { text: directionText; font.pixelSize: 24; font.bold: true; color: settingsManager.darkMode ? Theme.darkText : Theme.lightText }
                            }

                            Column {
                                spacing: 4
                                Text { text: "Wind Speed"; font.pixelSize: 18; color: settingsManager.darkMode ? Theme.darkText : Theme.lightText }
                                Text { text: speedText; font.pixelSize: 24; font.bold: true; color: settingsManager.darkMode ? Theme.darkText : Theme.lightText }
                            }
                        }
                    }

                    RowLayout {
                        spacing: 12
                        Layout.alignment: Qt.AlignHCenter

                        Button {
                            text: "+15m"
                            checkable: true
                            checked: true
                            onClicked: {
                                windPredictionModel.setHorizon("15m")
                                horizon15.checked = true
                                horizon1h.checked = false
                                horizon3h.checked = false
                                horizon6h.checked = false
                            }
                            id: horizon15
                        }

                        Button {
                            text: "+1h"
                            checkable: true
                            onClicked: {
                                windPredictionModel.setHorizon("1h")
                                horizon15.checked = false
                                horizon1h.checked = true
                                horizon3h.checked = false
                                horizon6h.checked = false
                            }
                            id: horizon1h
                        }

                        Button {
                            text: "+3h"
                            checkable: true
                            onClicked: {
                                windPredictionModel.setHorizon("3h")
                                horizon15.checked = false
                                horizon1h.checked = false
                                horizon3h.checked = true
                                horizon6h.checked = false
                            }
                            id: horizon3h
                        }

                        Button {
                            text: "+6h"
                            checkable: true
                            onClicked: {
                                windPredictionModel.setHorizon("6h")
                                horizon15.checked = false
                                horizon1h.checked = false
                                horizon3h.checked = false
                                horizon6h.checked = true
                            }
                            id: horizon6h
                        }
                    }

                    Button {
                        text: "🔮 Predict"
                        font.pixelSize: 16
                        width: 220
                        height: 42
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: windPredictionModel.predictNow()
                    }

                    Text {
                        text: bufferStatusText
                        font.pixelSize: 16
                        color: bufferStatusText.startsWith("✅") ? "green" : "orange"
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
                Flickable {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    contentWidth: chartsContainer.implicitWidth
                    contentHeight: chartsContainer.implicitHeight
                    interactive: true

                    ColumnLayout {
                        id: chartsContainer
                        width: parent.width
                        spacing: 12

                        // === Component untuk Label Direction +15m ===
                        Component {
                            id: dirLabelOverlay
                            Item {
                                width: dirChart.width
                                height: dirChart.height

                                Repeater {
                                    model: dirChartModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? dirChart.mapToPosition(Qt.point(modelData.index, modelData.value), series15mDir)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(1) + "°" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }
                        // === Component untuk Label Speed +15m ===
                        Component {
                            id: speedLabelOverlay
                            Item {
                                width: speedChart.width
                                height: speedChart.height

                                Repeater {
                                    model: speedChartModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? speedChart.mapToPosition(Qt.point(modelData.index, modelData.value), series15mSpeed)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(2) + " m/s" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }

                        Component {
                            id: dirLabelOverlay1h
                            Item {
                                width: dirChart1h.width
                                height: dirChart1h.height

                                Repeater {
                                    model: chart1hDirModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? dirChart1h.mapToPosition(Qt.point(modelData.index, modelData.value), series1hDir)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(1) + "°" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }
                        Component {
                            id: speedLabelOverlay1h
                            Item {
                                width: speedChart1h.width
                                height: speedChart1h.height

                                Repeater {
                                    model: chart1hSpeedModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? speedChart1h.mapToPosition(Qt.point(modelData.index, modelData.value), series1hSpeed)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(2) + " m/s" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }
                        Component {
                            id: dirLabelOverlay3h
                            Item {
                                width: dirChart3h.width
                                height: dirChart3h.height

                                Repeater {
                                    model: chart3hDirModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? dirChart3h.mapToPosition(Qt.point(modelData.index, modelData.value), series3hDir)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(1) + "°" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }
                        Component {
                            id: speedLabelOverlay3h
                            Item {
                                width: speedChart3h.width
                                height: speedChart3h.height

                                Repeater {
                                    model: chart3hSpeedModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? speedChart3h.mapToPosition(Qt.point(modelData.index, modelData.value), series3hSpeed)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(2) + " m/s" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }
                        Component {
                            id: dirLabelOverlay6h
                            Item {
                                width: dirChart6h.width
                                height: dirChart6h.height

                                Repeater {
                                    model: chart6hDirModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? dirChart6h.mapToPosition(Qt.point(modelData.index, modelData.value), series6hDir)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(1) + "°" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }
                        Component {
                            id: speedLabelOverlay6h
                            Item {
                                width: speedChart6h.width
                                height: speedChart6h.height

                                Repeater {
                                    model: chart6hSpeedModel
                                    delegate: Item {
                                        width: 1; height: 1

                                        property var pt: (typeof modelData.value === 'number')
                                                        ? speedChart6h.mapToPosition(Qt.point(modelData.index, modelData.value), series6hSpeed)
                                                        : Qt.point(0, 0)

                                        Text {
                                            visible: modelData.value !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 30
                                            text: modelData.value !== undefined ? modelData.value.toFixed(2) + " m/s" : "-"
                                            font.pixelSize: 12
                                            font.bold: true
                                            color: settingsManager.darkMode ? "white" : "black"
                                            z: 100
                                        }

                                        Text {
                                            visible: modelData.timestamp !== undefined && !isNaN(pt.x) && !isNaN(pt.y)
                                            x: pt.x - 15
                                            y: pt.y - 15
                                            text: modelData.timestamp !== undefined ? modelData.timestamp : "-"
                                            font.pixelSize: 10
                                            color: "gray"
                                            z: 100
                                        }
                                    }
                                }
                            }
                        }

                        GridLayout {
                            columns: 2
                            rowSpacing: 12
                            columnSpacing: 12
                            Layout.alignment: Qt.AlignTop
                            anchors.horizontalCenter: parent.horizontalCenter

                            // === +15m Direction Chart ===
                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: dirChart
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis15d; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis15d; min: 0; max: 360; titleText: "°" }

                                    LineSeries {
                                        id: series15mDir
                                        axisX: xAxis15d
                                        axisY: yAxis15d
                                        name: "+15m Direction"
                                        color: "orange"
                                        pointsVisible: true
                                    }
                                }
                                // === LABEL OVERLAY UNTUK DIRECTION +15m ===
                                Loader {
                                    id: dirLabels
                                    active: showDirLabels
                                    asynchronous: true
                                    sourceComponent: dirLabelOverlay
                                }
                            }


                            // === +15m Speed Chart ===
                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: speedChart
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis15s; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis15s; min: 0; max: 10; titleText: "m/s" }

                                    LineSeries {
                                        id: series15mSpeed
                                        axisX: xAxis15s
                                        axisY: yAxis15s
                                        name: "+15m Speed"
                                        color: "teal"
                                        pointsVisible: true
                                    }
                                }
                                // === LABEL OVERLAY UNTUK SPEED +15m ===
                                Loader {
                                    id: speedLabels
                                    active: showSpeedLabels
                                    asynchronous: true
                                    sourceComponent: speedLabelOverlay
                                }                                
                            }


                            // === 1h Charts ===
                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: dirChart1h
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis1d; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis1d; min: 0; max: 360; titleText: "°" }

                                    LineSeries {
                                        id: series1hDir
                                        axisX: xAxis1d
                                        axisY: yAxis1d
                                        pointsVisible: true
                                        color: "orange"
                                        name: "+1h Direction"
                                    }
                                }

                                Loader {
                                    id: dirLabels1h
                                    active: show1hLabels
                                    asynchronous: true
                                    sourceComponent: dirLabelOverlay1h
                                }
                            }


                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: speedChart1h
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis1s; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis1s; min: 0; max: 10; titleText: "m/s" }

                                    LineSeries {
                                        id: series1hSpeed
                                        axisX: xAxis1s
                                        axisY: yAxis1s
                                        pointsVisible: true
                                        color: "teal"
                                        name: "+1h Speed"
                                    }
                                }

                                Loader {
                                    id: speedLabels1h
                                    active: show1hLabels
                                    asynchronous: true
                                    sourceComponent: speedLabelOverlay1h
                                }
                            }

                            // === 3h Charts ===
                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: dirChart3h
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis3d; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis3d; min: 0; max: 360; titleText: "°" }

                                    LineSeries {
                                        id: series3hDir
                                        axisX: xAxis3d
                                        axisY: yAxis3d
                                        pointsVisible: true
                                        color: "orange"
                                        name: "+3h Direction"
                                    }
                                }

                                Loader {
                                    id: dirLabels3h
                                    active: show3hLabels
                                    asynchronous: true
                                    sourceComponent: dirLabelOverlay3h
                                }
                            }

                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: speedChart3h
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis3s; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis3s; min: 0; max: 10; titleText: "m/s" }

                                    LineSeries {
                                        id: series3hSpeed
                                        axisX: xAxis3s
                                        axisY: yAxis3s
                                        pointsVisible: true
                                        color: "teal"
                                        name: "+3h Speed"
                                    }
                                }

                                Loader {
                                    id: speedLabels3h
                                    active: show3hLabels
                                    asynchronous: true
                                    sourceComponent: speedLabelOverlay3h
                                }
                            }

                            // === 6h Charts ===
                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: dirChart6h
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis6d; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis6d; min: 0; max: 360; titleText: "°" }

                                    LineSeries {
                                        id: series6hDir
                                        axisX: xAxis6d
                                        axisY: yAxis6d
                                        pointsVisible: true
                                        color: "orange"
                                        name: "+6h Direction"
                                    }
                                }

                                Loader {
                                    id: dirLabels6h
                                    active: show6hLabels
                                    asynchronous: true
                                    sourceComponent: dirLabelOverlay6h
                                }
                            }

                            Item {
                                Layout.preferredWidth: 500
                                Layout.preferredHeight: 300
                                Layout.alignment: Qt.AlignHCenter

                                ChartView {
                                    id: speedChart6h
                                    anchors.fill: parent
                                    clip: true
                                    antialiasing: true
                                    theme: settingsManager.darkMode ? ChartView.ChartThemeDark : ChartView.ChartThemeLight

                                    ValueAxis { id: xAxis6s; min: 0; max: 4; titleText: "Index" }
                                    ValueAxis { id: yAxis6s; min: 0; max: 10; titleText: "m/s" }

                                    LineSeries {
                                        id: series6hSpeed
                                        axisX: xAxis6s
                                        axisY: yAxis6s
                                        pointsVisible: true
                                        color: "teal"
                                        name: "+6h Speed"
                                    }
                                }

                                Loader {
                                    id: speedLabels6h
                                    active: show6hLabels
                                    asynchronous: true
                                    sourceComponent: speedLabelOverlay6h
                                }
                            }
                        }
                    }    
                }   
            }
        }
    }

    PropertyAnimation {
        id: angleAnim
        target: needle
        property: "rotation"
        duration: 600
        easing.type: Easing.InOutQuad
    }
}
