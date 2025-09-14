import os
from cuacane_app.utils.convert_to_mh2 import batch_convert

def test_batch_convert():
    input_file = os.path.join("cuacane_app", "test", "realtime_log.csv")
    output_file = os.path.join("cuacane_app", "test", "output.mh2")

    if os.path.exists(output_file):
        os.remove(output_file)

    batch_convert(input_file, output_file)

    assert os.path.exists(output_file), "❌ File MH2 tidak dibuat!"

    with open(output_file, 'r') as f:
        lines = f.readlines()

    print("[DEBUG] Isi file MH2:")
    for i, line in enumerate(lines):
        print(f"{i}: {line.strip()}")

    assert lines[0].strip() == "TIME,DIR,SPEED,TEMP,HUM,PRES", "❌ Header tidak sesuai!"
    assert len(lines) >= 3, "❌ Baris data tidak cukup!"
    assert lines[1].count(",") == 5, "❌ Format baris data tidak valid!"

    print("✅ Konversi MH2 berhasil dan hasil valid!")

if __name__ == "__main__":
    test_batch_convert()
