        maps_page = QWidget()
        maps_page.setLayout(None)  # NON-layout to allow overlapping widgets

        # Leaflet Map (background)
        self.leaflet_maps_widget = LeafletMapsWidget()
        self.leaflet_maps_widget.setParent(maps_page)
        self.leaflet_maps_widget.setGeometry(0, 0, self.width(), self.height())
        self.leaflet_maps_widget.setMinimumSize(600, 400)

        # QML Overlay (form)
        maps_qml = QQuickWidget()
        maps_qml.setResizeMode(QQuickWidget.SizeRootObjectToView)
        maps_qml.setClearColor(Qt.transparent)
        maps_qml.setAttribute(Qt.WA_TranslucentBackground)
        maps_qml.setStyleSheet("background: transparent;")
        maps_qml.setAttribute(Qt.WA_AlwaysStackOnTop)
        maps_qml.setFocusPolicy(Qt.StrongFocus)
        maps_qml.setFocus()
        maps_qml.setParent(maps_page)
        maps_qml.setGeometry(0, 0, self.width(), self.height())  # Tumpuk di atas

        maps_qml.rootContext().setContextProperty("sensorManager", self.sensor_manager)
        maps_qml.setSource(QUrl("views/MapsPage.qml"))