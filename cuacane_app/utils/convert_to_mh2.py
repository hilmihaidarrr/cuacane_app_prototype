import csv
from datetime import datetime
import os

def batch_convert(input_path: str, output_path: str):
    """
    Mengubah file realtime_log.csv menjadi format .MH2
    Format output mengikuti struktur yang dibutuhkan oleh PC-COSYMA
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file tidak ditemukan: {input_path}")

    with open(input_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    if not rows:
        raise ValueError("File log kosong")

    with open(output_path, 'w') as out_file:
        out_file.write("TIME,DIR,SPEED,TEMP,HUM,PRES\n")  # Header file MH2

        for row in rows:
            try:
                timestamp = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S")
                hour = timestamp.strftime("%H:%M")
                direction = float(row["wind_dir_avg"])
                speed = float(row["wind_speed_avg"])
                temp = float(row["temp_air"])
                humidity = float(row["humidity"])
                pressure = float(row["pressure"]) * 1000  # dari B ke Pa

                out_file.write(f"{hour},{direction:.1f},{speed:.2f},{temp:.1f},{humidity:.1f},{pressure:.0f}\n")

            except Exception as e:
                print(f"[!] Lewatkan baris: {e}")
