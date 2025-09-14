import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 960
    height: 640
    title: qsTr("Cuacane")
    color: "#fefefe"

    // ⬇️ Pastikan DashboardPage.qml sudah ada
    DashboardPage {
        anchors.fill: parent
    }
}
