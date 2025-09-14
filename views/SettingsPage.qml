import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import AppTheme 1.0

Item {
    id: settingsPage
    width: 800
    height: 600

    property bool isConnecting: false

    Rectangle {
        anchors.fill: parent
        color: settingsManager.darkMode ? Theme.darkBackground : Theme.lightBackground

        Rectangle {
            id: card
            width: 400
            height: 500   // ditambah supaya muat footer
            radius: 16
            color: settingsManager.darkMode ? "#1e1e1e" : "#ffffff"
            anchors.centerIn: parent
            border.color: settingsManager.darkMode ? "#2a2a2a" : "#cccccc"
            border.width: 1

            layer.enabled: true
            layer.effect: DropShadow {
                color: "#00000088"
                radius: 16
                samples: 32
                verticalOffset: 6
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 20

                // Title
                RowLayout {
                    spacing: 8
                    Layout.alignment: Qt.AlignHCenter

                    Label {
                        text: "\u2699"
                        font.pixelSize: 28
                        color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                    }

                    Label {
                        text: "Settings"
                        font.pixelSize: 24
                        font.bold: true
                        color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                    }
                }

                // Connection Status
                RowLayout {
                    spacing: 10
                    Layout.alignment: Qt.AlignHCenter

                    Label {
                        text: sensorManager && sensorManager.is_connected ? "\u{1F4F6}" : "\u{26D4}"
                        font.pixelSize: 20
                        color: sensorManager && sensorManager.is_connected ? "lightgreen" : "tomato"
                    }

                    Label {
                        id: statusLabel
                        text: sensorManager && sensorManager.is_connected ? "Connected to Sensor" : "Not Connected"
                        font.pixelSize: 16
                        color: sensorManager && sensorManager.is_connected ? "lightgreen" : "tomato"
                    }

                    BusyIndicator {
                        running: isConnecting
                        visible: isConnecting
                        width: 18
                        height: 18
                    }
                }

                // Reconnect Button
                Button {
                    text: sensorManager && sensorManager.is_connected ? "Connected" : "Try to Connect"
                    enabled: sensorManager && !sensorManager.is_connected
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        isConnecting = true
                        statusLabel.text = "Connecting..."
                        let result = sensorManager.connect()
                        statusLabel.text = result
                        isConnecting = false
                    }
                }

                // Dark Mode Toggle
                RowLayout {
                    spacing: 12
                    Layout.alignment: Qt.AlignHCenter

                    Label {
                        text: "\u{1F319} Dark Mode:"
                        font.pixelSize: 16
                        color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                    }

                    Switch {
                        checked: settingsManager.darkMode
                        onToggled: settingsManager.setDarkMode(checked)
                    }
                }

                // UI Scale Options
                GroupBox {
                    title: "UI Scale"
                    Layout.fillWidth: true

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        RadioButton {
                            text: "Small"
                            Layout.fillWidth: true
                            checked: settingsManager.uiScale === 0.8
                            onClicked: settingsManager.setUiScale(0.8)
                        }

                        RadioButton {
                            text: "Normal"
                            Layout.fillWidth: true
                            checked: settingsManager.uiScale === 1.0
                            onClicked: settingsManager.setUiScale(1.0)
                        }

                        RadioButton {
                            text: "Large"
                            Layout.fillWidth: true
                            checked: settingsManager.uiScale === 1.25
                            onClicked: settingsManager.setUiScale(1.25)
                        }
                    }
                }

                // Spacer agar footer tetap di bawah
                Item { Layout.fillHeight: true }


                // Footer "Developed by"
                Label {
                    text: "Developed by: Hilmi, Nabila, Thoriq"
                    font.pixelSize: 14
                    color: settingsManager.darkMode ? "#aaaaaa" : "#666666"
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
