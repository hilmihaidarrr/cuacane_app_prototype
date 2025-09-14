from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, QSettings, pyqtSlot

class SettingsManager(QObject):
    darkModeChanged = pyqtSignal()
    languageIndexChanged = pyqtSignal()
    uiScaleChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings("CuacaneApp", "UserPreferences")
        self._dark_mode = self.settings.value("darkMode", False, type=bool)
        self._language_index = self.settings.value("languageIndex", 0, type=int)
        self._ui_scale = self.settings.value("uiScale", 1.0, type=float)  # ✅ Tambahan

    @pyqtProperty(bool, notify=darkModeChanged)
    def darkMode(self):
        return self._dark_mode

    @pyqtSlot(bool)
    def setDarkMode(self, value):
        if self._dark_mode != value:
            self._dark_mode = value
            self.settings.setValue("darkMode", value)
            self.darkModeChanged.emit()

    @pyqtProperty(int, notify=languageIndexChanged)
    def languageIndex(self):
        return self._language_index

    @pyqtSlot(int)
    def setLanguageIndex(self, value):
        if self._language_index != value:
            self._language_index = value
            self.settings.setValue("languageIndex", value)
            self.languageIndexChanged.emit()

    # ✅ UI Scale Property
    @pyqtProperty(float, notify=uiScaleChanged)
    def uiScale(self):
        return self._ui_scale

    @pyqtSlot(float)
    def setUiScale(self, scale):
        if self._ui_scale != scale:
            self._ui_scale = scale
            self.settings.setValue("uiScale", scale)
            self.uiScaleChanged.emit()
