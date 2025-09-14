from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, QUrl, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import json

class WebBridge(QObject):
    sendPlumeData = pyqtSignal(str)

    @pyqtSlot()
    def jsReady(self):
        print("[🌐] JavaScript siap menerima data")


class LeafletMapsWidget(QWidget):
    def __init__(self):
        super().__init__()
        print("[DEBUG] Masuk ke LeafletMapsWidget.__init__()")

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.browser = QWebEngineView()
        self.bridge = WebBridge()
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.browser.page().setWebChannel(self.channel)

        # Aktifkan handler untuk console.log di JS
        self.browser.page().javaScriptConsoleMessage = self.handle_js_console

        QTimer.singleShot(0, self.load_browser)

    def handle_js_console(self, level, message, lineNumber, sourceID):
        print(f"[JS CONSOLE] Line {lineNumber} | {message}")

    def load_browser(self):
        print("[DEBUG] Membuat QWebEngineView setelah QApplication idle")
        try:
            html = self.get_leaflet_html()
            print("[DEBUG] HTML berhasil digenerate, panjang:", len(html))
            self.browser.setHtml(html, QUrl("qrc:/"))
            print("[DEBUG] setHtml() dipanggil")
        except Exception as e:
            print("[ERROR] Gagal memuat HTML ke QWebEngineView:", str(e))

        self.layout.addWidget(self.browser)

    def update_plume(self, X, Y, C):
        print("[📡] Mengirim data plume ke JavaScript (lama)")
        plume_data = {"x": X.tolist(), "y": Y.tolist(), "c": C.tolist()}
        self.bridge.sendPlumeData.emit(json.dumps(plume_data))

    def sendHeatmapData(self, points):
        """
        Kirim data heatmap ke peta dalam format [[lat, lon, intensity], ...]
        """
        try:
            js_payload = json.dumps(points)
            print(f"[DEBUG] Menjalankan updateHeatmap() dengan {len(points)} titik")
            self.browser.page().runJavaScript(f"updateHeatmap({js_payload});")
            print("[📡] Heatmap berhasil dikirim ke map lewat runJavaScript()")
        except Exception as e:
            print(f"[❌] Gagal kirim heatmap: {e}")

    def get_leaflet_html(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Peta Cuacane</title>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\" />
            <script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script>
            <script src=\"https://unpkg.com/leaflet.heat/dist/leaflet-heat.js\"></script>
            <script src=\"qrc:///qtwebchannel/qwebchannel.js\"></script>
            <style>
                html, body, #map { height: 100%; margin: 0; padding: 0; }
            </style>
        </head>
        <body>
            <div id=\"map\"></div>
            <script>
                console.log("📍 Memulai skrip JavaScript Peta Cuacane...");

                var map = L.map('map').setView([-6.8877831363571, 107.60727549580955], 16);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }).addTo(map);
                L.marker([-6.8877831363571, 107.60727549580955])
                    .addTo(map)
                    .bindPopup("Sensor Vaisala WXT520").openPopup();

                var heatLayer = null;
                window.heatmapReady = false;

                function updateHeatmap(points) {
                    const size = map.getSize();
                    if (!window.heatmapReady || size.x === 0 || size.y === 0) {
                        console.warn("⏳ Menunda heatmap: map belum siap ukurannya...");
                        setTimeout(() => updateHeatmap(points), 100);
                        return;
                    }

                    if (heatLayer) map.removeLayer(heatLayer);

                    console.log("🔥 updateHeatmap() dipanggil dgn", points.length, "titik");
                    heatLayer = L.heatLayer(points, {
                        radius: 25,
                        blur: 15,
                        maxZoom: 17,
                        gradient: {
                            0.0: 'blue',
                            0.5: 'lime',
                            1.0: 'red'
                        }
                    }).addTo(map);
                }


                map.whenReady(() => {
                    console.log("✅ Leaflet map siap!");
                    window.heatmapReady = true;
                });

                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.bridge = channel.objects.bridge;
                    console.log("✅ WebChannel connected");

                    bridge.sendPlumeData.connect(function(jsonStr) {
                        console.log("📨 Menerima data dari PyQt:", jsonStr);
                        var data = JSON.parse(jsonStr);
                        var points = [];
                        for (var i = 0; i < data.x.length; i++) {
                            points.push([data.y[i], data.x[i], data.c[i]]);
                        }
                        updateHeatmap(points);
                    });

                    bridge.jsReady();
                });
            </script>
        </body>
        </html>
        """
