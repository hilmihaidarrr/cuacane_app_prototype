import os
import csv
import time
from datetime import datetime
from cuacane_app.utils.sensor_connection import append_to_log

def test_append_to_log():
    from cuacane_app.utils.sensor_connection import append_to_log
    import csv, os

    log_path = "cuacane_app/data_logs/realtime_log.csv"
    if os.path.exists(log_path):
        os.remove(log_path)

    dummy_data = {
        "timestamp": "2025-07-29 19:45",
        "temp_air": 25.3,
        "humidity": 68.2,
        "pressure": 0.923,
        "wind_speed_avg": 1.5,
        "wind_dir_avg": 270,
    }

    append_to_log(dummy_data)
    append_to_log(dummy_data)  # Duplikat, harus diabaikan

    with open(log_path, "r") as file:
        reader = list(csv.DictReader(file))
        print(f"[ℹ️] Total entri: {len(reader)}")
        assert len(reader) == 1, "❌ Duplikasi belum dicegah dengan benar!"
    
    print("✅ Test data logger berhasil.")



if __name__ == "__main__":
    test_append_to_log()
