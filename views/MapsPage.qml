// cuacane_app/views/MapsPage.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtWebEngine 1.7
import QtGraphicalEffects 1.15

Item {
    id: root
    anchors.fill: parent

    property var latestHeatmapData: null
    property real inputQValue: 0.0
    property real inputHValue: 0.0
    property bool isSimulating: false

    WebEngineView {
        id: mapView
        objectName: "mapView"
        anchors.fill: parent
        url: Qt.resolvedUrl("map.html")

        onLoadingChanged: {
            if (loadRequest.status === WebEngineLoadRequest.LoadSucceededStatus && latestHeatmapData !== null) {
                console.log("✅ map.html loaded, sending heatmap...");
                mapView.runJavaScript("updateHeatmap(" + latestHeatmapData + ")")
            }
        }
    }

    Rectangle {
        id: overlayCard
        width: 280
        height: 220
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 16
        radius: 10
        color: "#ffffffe0"
        border.color: "#aaa"
        border.width: 1

        
        property string qUnit: "Bq/s"
        property string hUnit: "m"

        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 1
            verticalOffset: 2
            radius: 6
            color: "#99999988"
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 8

            Label {
                text: "Distribution simulation"
                font.pixelSize: 16
                font.bold: true
            }

            // ------- Input Q + unit di kanan -------
            RowLayout {
                spacing: 8
                Layout.fillWidth: true

                TextField {
                    id: inputQ
                    Layout.fillWidth: true
                    placeholderText: "Value Q"
                    text: inputQValue.toString()
                    onTextChanged: {
                        const val = parseFloat(text)
                        if (!isNaN(val)) inputQValue = val
                    }
                    validator: DoubleValidator { bottom: 0.0 }
                }

                Label {
                    text: overlayCard.qUnit
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // ------- Input H + unit di kanan -------
            RowLayout {
                spacing: 8
                Layout.fillWidth: true

                TextField {
                    id: inputH
                    Layout.fillWidth: true
                    placeholderText: "Height H"
                    text: inputHValue.toString()
                    onTextChanged: {
                        const val = parseFloat(text)
                        if (!isNaN(val)) inputHValue = val
                    }
                    validator: DoubleValidator { bottom: 0.0 }
                }

                Label {
                    text: overlayCard.hUnit
                    verticalAlignment: Text.AlignVCenter
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignRight
                spacing: 8

                Button {
                    text: "Delete Spread"
                    onClicked: {
                        mapView.runJavaScript("if (typeof heatLayer !== 'undefined') { map.removeLayer(heatLayer); heatLayer = null; console.log('[🧹] Heatmap cleared'); }")
                        latestHeatmapData = null
                    }
                }

                Button {
                    text: isSimulating ? "Stop" : "Start"
                    onClicked: {
                        if (isSimulating) {
                            sensorManager.stopDispersionLoop()
                            isSimulating = false
                        } else {
                            sensorManager.startDispersionLoop(inputQValue, inputHValue)
                            isSimulating = true
                        }
                    }
                }
            }
        }

        Component.onCompleted: inputQ.focus = true
    }

    function updateHeatmapFromPython(jsonString) {
        console.log("📨 Menerima heatmap dari Python");
        latestHeatmapData = jsonString;
        mapView.runJavaScript("updateHeatmap(" + jsonString + ")")
    }

    // === Perbaiki Connections: gunakan function handler ===
    Connections {
        target: sensorManager
        function onLatestDataChanged() {
            isSimulating = sensorManager.isDispersionRunning
        }
    }

    Connections {
        target: sensorManager
        // misal sinyal: simulationFailed(string msg)
        function onSimulationFailed(msg) {
            console.log("⚠️ Simulasi gagal: " + msg)
            failedText.text = msg
            simulationFailedDialog.open()
        }
    }

    Dialog {
        id: simulationFailedDialog
        title: "Simulasi Gagal"
        modal: true
        visible: false
        focus: true
        standardButtons: Dialog.Ok

        Column {
            spacing: 8
            padding: 16
            Label {
                id: failedText
                text: ""
                wrapMode: Text.Wrap
            }
        }

        onAccepted: close()

        Timer {
            interval: 3000
            running: simulationFailedDialog.visible
            repeat: false
            onTriggered: simulationFailedDialog.close()
        }
    }
}
