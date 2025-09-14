import QtQuick 2.15
import QtCharts 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import AppTheme 1.0

Item {
    id: dashboardPage
    width: parent ? parent.width : 1920
    height: parent ? parent.height : 1080

    property var currentData: sensorManager.latest_data_qml
    property string selectedParameter: "temp_air"
    property var chartModel: []
    property bool showLabels: true
    property real scaleFactor: settingsManager.uiScale

    scale: scaleFactor

    Rectangle {
        anchors.fill: parent
        color: settingsManager.darkMode ? Theme.darkBackground : Theme.lightBackground

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24 * scaleFactor
            spacing: 20 * scaleFactor

            // === Header ===
            RowLayout {
                width: parent.width

                Label {
                    text: "📡 WXT520 Sensor Data"
                    font.pixelSize: 28 * scaleFactor
                    font.bold: true
                    color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                }

                Item { Layout.fillWidth: true }

                Label {
                    id: clockLabel
                    text: Qt.formatDateTime(new Date(), "dddd, dd MMMM yyyy - hh:mm:ss")
                    font.pixelSize: 22 * scaleFactor
                    font.bold: true
                    color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                }

                Timer {
                    interval: 1000; running: true; repeat: true
                    onTriggered: clockLabel.text = Qt.formatDateTime(new Date(), "dddd, dd MMMM yyyy - hh:mm:ss")
                }
            }

            // === Grid Info Cards ===
            GridLayout {
                id: cardGrid
                columns: Math.max(2, Math.min(4, Math.floor(dashboardPage.width / (250 * scaleFactor))))
                rowSpacing: 16 * scaleFactor
                columnSpacing: 16 * scaleFactor
                Layout.alignment: Qt.AlignHCenter

                Repeater {
                    model: [
                        { title: "Air temperature", key: "temp_air", value: currentData.temp_air + "°C", icon: "🌡" },
                        { title: "Air humidity", key: "humidity", value: currentData.humidity + "%", icon: "💧" },
                        { title: "Air pressure", key: "pressure", value: currentData.pressure + " hPa", icon: "📟" },
                        { title: "Is it Rain?", key: "rain_accum", value: currentData.rain_accum > 0 ? "Yes" : "No", icon: "☔" },
                        { title: "Rain Intensity", key: "rain_intensity", value: currentData.rain_intensity + " mm/h", icon: "🌧" },
                        { title: "Rain Accumulation", key: "rain_accum", value: currentData.rain_accum + " mm", icon: "🌧" },
                        { title: "Wind Speed", key: "wind_speed_avg", value: currentData.wind_speed_avg + " m/s", icon: "🌬" },
                        { title: "Wind Direction (directed From)", key: "wind_dir_avg", value: currentData.wind_dir_avg + "°", icon: "🧭" }
                    ]

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 180 * scaleFactor
                        Layout.minimumWidth: 180 * scaleFactor
                        radius: 10 * scaleFactor
                        color: settingsManager.darkMode ? "#1e1e1e" : "#ffffff"
                        border.color: "#ccc"
                        border.width: 1

                        layer.enabled: true
                        layer.effect: DropShadow {
                            color: "#00000066"
                            radius: 8 * scaleFactor
                            samples: 16
                            verticalOffset: 4 * scaleFactor
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                selectedParameter = modelData.key
                                updateGraph(selectedParameter)
                            }
                        }

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12 * scaleFactor
                            spacing: 8 * scaleFactor

                            Text {
                                text: modelData.icon
                                font.pixelSize: 34 * scaleFactor
                                horizontalAlignment: Text.AlignHCenter
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Label {
                                text: modelData.title
                                font.pixelSize: 18 * scaleFactor
                                horizontalAlignment: Text.AlignHCenter
                                Layout.alignment: Qt.AlignHCenter
                                color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                            }

                            Label {
                                text: modelData.value !== undefined ? modelData.value : "-"
                                font.pixelSize: 22 * scaleFactor
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                                Layout.alignment: Qt.AlignHCenter
                                color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                            }
                        }
                    }
                }
            }

            // === Grafik History + Label Overlay ===
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ChartView {
                    id: chartView
                    anchors.fill: parent
                    antialiasing: true
                    backgroundColor: settingsManager.darkMode ? "#1e1e1e" : "#ffffff"
                    title: "History: " + selectedParameter
                    titleFont.pixelSize: 20 * scaleFactor

                    ValueAxis { id: xAxis; min: 0; max: 14; titleText: "Index" }
                    ValueAxis { id: yAxis; min: 0; max: 14; titleText: "Value" }

                    LineSeries {
                        id: series
                        axisX: xAxis
                        axisY: yAxis
                        name: selectedParameter
                        pointsVisible: true
                    }
                }


                Loader {
                    id: chartLabels
                    active: showLabels
                    asynchronous: true
                    sourceComponent: labelOverlayComponent
                }

                Component {
                    id: labelOverlayComponent

                    Item {
                        width: parent.width
                        height: parent.height

                        Repeater {
                            model: chartModel
                            delegate: Item {
                                width: 1; height: 1

                                property var pt: (typeof modelData.value === 'number' && !isNaN(modelData.value))
                                                ? chartView.mapToPosition(Qt.point(modelData.index, modelData.value), series)
                                                : Qt.point(0, 0)

                                Text {
                                    visible: !isNaN(pt.x) && !isNaN(pt.y)
                                    x: pt.x - 15 * scaleFactor
                                    y: pt.y - 30 * scaleFactor
                                    text: (typeof modelData.value === "number") ? modelData.value.toFixed(2) : "-"
                                    font.pixelSize: 12 * scaleFactor
                                    color: settingsManager.darkMode ? Theme.darkText : "black"
                                    z: 100
                                }

                                Text {
                                    visible: !isNaN(pt.x) && !isNaN(pt.y)
                                    x: pt.x - 15 * scaleFactor
                                    y: pt.y - 15 * scaleFactor
                                    text: modelData.timestamp !== undefined ? modelData.timestamp : ""
                                    font.pixelSize: 10 * scaleFactor
                                    color: settingsManager.darkMode ? "#aaa" : "gray"
                                    z: 100
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: sensorManager
        function onLatestDataChanged() {
            updateGraph(selectedParameter)
        }
    }

    function updateChartModel(paramKey) {
        chartModel = []
        var history = sensorManager["history_" + paramKey] || []
        var timestamp = Qt.formatTime(new Date(), "hh:mm:ss")
        for (var i = 0; i < history.length; ++i) {
            chartModel.push({ index: i, value: history[i], timestamp: timestamp })
        }
    }

    // --- Update fungsi updateGraph() ---
    function updateGraph(paramKey) {
        series.clear()
        chartModel = []

        var history = sensorManager["history_" + paramKey] || []
        var limitedHistory = history.slice(-15)

        var minY = Number.POSITIVE_INFINITY
        var maxY = Number.NEGATIVE_INFINITY

        for (var i = 0; i < limitedHistory.length; ++i) {
            let item = limitedHistory[i]
            let val = (typeof item === 'object') ? item.value : item
            let timeLabel = (typeof item === 'object') ? item.timestamp : Qt.formatTime(new Date(), "hh:mm")

            if (typeof val === "number" && isFinite(val)) {
                series.append(i, val)
                chartModel.push({ index: i, value: val, timestamp: timeLabel })
                if (val < minY) minY = val
                if (val > maxY) maxY = val
            } else {
                // tetap push timestamp agar overlay tidak error
                chartModel.push({ index: i, value: NaN, timestamp: timeLabel })
            }
        }

        // fallback jika belum ada data valid
        if (!isFinite(minY) || !isFinite(maxY)) {
            minY = 0
            maxY = 1
        }

        // padding 20% dari rentang
        var pad = Math.max( (maxY - minY) * 0.2, 0.1 )

        // Param yang harus mulai dari 0
        var forceZeroMin = (paramKey === "rain_intensity" ||
                            paramKey === "rain_accum" ||
                            paramKey === "wind_speed_avg")

        if (forceZeroMin) {
            yAxis.min = 0
        } else {
            yAxis.min = minY - pad
        }
        yAxis.max = maxY + pad

        // X axis: dari 0 sampai jumlah titik-1 (min 10 supaya enak dilihat)
        xAxis.min = 0
        xAxis.max = Math.max(limitedHistory.length - 1, 10)

        // Refresh overlay label (timestamp di atas titik)
        showLabels = false
        Qt.callLater(function(){ showLabels = true })
    }
}
