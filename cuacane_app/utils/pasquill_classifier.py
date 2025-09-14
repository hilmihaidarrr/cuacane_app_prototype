from datetime import datetime

class PasquillStabilityClassifier:
    """
    Kelas untuk menentukan stabilitas atmosfer (A–F) berdasarkan metode Pasquill,
    dengan input dari data sensor Cuacane.
    """

    @staticmethod
    def classify_solar_insolation(air_temp, relative_humid, hour):
        """Klasifikasi radiasi matahari berdasarkan suhu, kelembapan, dan jam"""
        if 6 <= hour < 17:
            if air_temp > 25.6 and relative_humid > 79.4:
                return 'strong'
            elif air_temp > 21 and relative_humid > 57.4:
                return 'moderate'
            else:
                return 'weak'
        return 'N/A'

    @staticmethod
    def classify_night_cloudiness(rain_intensity, hour):
        """Klasifikasi kondisi awan saat malam berdasarkan hujan"""
        if hour < 6 or hour >= 17:
            if rain_intensity < 10:
                return 'clear'
            else:
                return 'cloudy'
        return 'N/A'

    @staticmethod
    def classify_windspeed_class(windspeed):
        """Klasifikasi kecepatan angin ke dalam kelas Pasquill"""
        if windspeed < 2:
            return '<2'
        elif 2 <= windspeed < 3:
            return '2-3'
        elif 3 <= windspeed < 5:
            return '3-5'
        elif 5 <= windspeed < 6:
            return '5-6'
        else:
            return '>6'

    @staticmethod
    def from_dict(data_dict: dict) -> str:
        """
        Fungsi utama untuk klasifikasi Pasquill dari dict hasil sensor Cuacane.
        Field yang dibutuhkan:
        - temp_air, humidity, rain_intensity, wind_speed_avg, datetime
        """
        try:
            temp = float(data_dict.get('temp_air', 0))
            humid = float(data_dict.get('humidity', 0))
            rain = float(data_dict.get('rain_intensity', 0))
            wind = float(data_dict.get('wind_speed_avg', 0))
            timestamp = data_dict.get('datetime', '')
            hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
        except Exception as e:
            print(f"[❌] Gagal parsing data untuk klasifikasi Pasquill: {e}")
            return 'D'  # Default

        wind_class = PasquillStabilityClassifier.classify_windspeed_class(wind)
        solar = PasquillStabilityClassifier.classify_solar_insolation(temp, humid, hour)
        night = PasquillStabilityClassifier.classify_night_cloudiness(rain, hour)

        # Logika utama Pasquill class
        if wind_class == '<2':
            if solar == 'strong':
                return 'A'
            elif solar == 'moderate':
                return 'B'
            elif solar == 'weak':
                return 'B'
            elif night == 'clear':
                return 'F'
            else:
                return 'E'
        elif wind_class == '2-3':
            if solar == 'strong':
                return 'A'
            elif solar == 'moderate':
                return 'B'
            elif solar == 'weak':
                return 'C'
            elif night == 'clear':
                return 'F'
            else:
                return 'D'
        elif wind_class == '3-5':
            if solar == 'strong':
                return 'B'
            elif solar == 'moderate':
                return 'B'
            elif solar == 'weak':
                return 'C'
            elif night == 'clear':
                return 'E'
            else:
                return 'D'
        elif wind_class == '5-6':
            if solar == 'strong':
                return 'C'
            elif solar == 'moderate':
                return 'C'
            elif solar == 'weak':
                return 'D'
            elif night == 'clear':
                return 'D'
            else:
                return 'D'
        else:
            if solar == 'strong':
                return 'C'
            elif solar == 'moderate':
                return 'D'
            elif solar == 'weak':
                return 'D'
            elif night == 'clear':
                return 'D'
            else:
                return 'D'
