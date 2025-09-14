import os
import stat

def make_files_readable(path, extensions=(".pth", ".pkl", ".csv")):
    for dirpath, _, filenames in os.walk(path):
        for fname in filenames:
            if fname.endswith(extensions):
                try:
                    full = os.path.join(dirpath, fname)
                    os.chmod(full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                except Exception as e:
                    print(f"[⚠️] Failed to set permission: {full} -> {e}")

# Lokasi folder saat run (saat di-bundle)
import sys
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    model_dir = os.path.join(base_dir, 'saved_models')
    log_dir = os.path.join(base_dir, 'cuacane_app', 'data_logs')
    make_files_readable(model_dir)
    make_files_readable(log_dir)
