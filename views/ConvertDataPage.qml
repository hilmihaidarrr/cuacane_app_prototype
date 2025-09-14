import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import AppTheme 1.0

Item {
    width: 800
    height: 600

    property string selectedFolder: ""

    Rectangle {
        anchors.fill: parent
        color: settingsManager.darkMode ? Theme.darkBackground : Theme.lightBackground

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            Text {
                text: "📁 Convert Sensor Data to .MH2"
                font.pixelSize: 24
                font.bold: true
                color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                Layout.alignment: Qt.AlignHCenter
            }

            Button {
                text: "📂 Select Output Folder"
                Layout.alignment: Qt.AlignHCenter
                onClicked: folderDialog.open()
            }

            Text {
                text: selectedFolder === "" ? "📄 No folders selected yet" : selectedFolder
                font.pixelSize: 16
                wrapMode: Text.Wrap
                color: settingsManager.darkMode ? Theme.darkText : Theme.lightText
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }

            Button {
                text: "🔄Start Conversion"
                Layout.alignment: Qt.AlignHCenter
                enabled: selectedFolder !== ""
                onClicked: {
                    convertSignalHandler.convertNow(selectedFolder)
                }
            }
        }

        FileDialog {
            id: folderDialog
            title: "Select Output Folder"
            selectFolder: true
            onAccepted: {
                selectedFolder = folderDialog.fileUrl.toString().replace("file:///", "").replace(/%20/g, " ")
            }
        }
    }
}
