import QtQuick 2.15

QtObject {
    // Warna latar utama aplikasi
    property color backgroundColor: settingsManager.darkMode ? "#121212" : "#ffffff"

    // Warna teks default
    property color textColor: settingsManager.darkMode ? "#eeeeee" : "#111111"

    // Warna latar elemen seperti kartu/info panel
    property color cardColor: settingsManager.darkMode ? "#1e1e1e" : "#f8f8f8"

    // Warna garis/border umum
    property color borderColor: settingsManager.darkMode ? "#444444" : "#cccccc"

    // Warna tombol dan elemen aksen
    property color accentColor: settingsManager.darkMode ? "#ff9800" : "#007acc"

    // Warna teks yang lebih redup (misal untuk label kecil)
    property color mutedText: settingsManager.darkMode ? "#aaaaaa" : "#666666"

    // Warna error / status
    property color errorColor: "#ff5555"
    property color successColor: "#00c853"
}
