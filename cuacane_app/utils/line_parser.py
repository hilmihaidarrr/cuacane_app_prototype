from datetime import datetime

def parse_0R0_line(payload: str) -> dict:
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data_parts = payload.strip().split(',')

        data_dict = {
            "datetime": now,
            "wind_dir_avg": None,
            "wind_dir_min": None,
            "wind_dir_max": None,
            "wind_speed_avg": None,
            "wind_speed_min": None,
            "wind_speed_max": None,
            "temp_air": None,
            "temp_probe": None,
            "humidity": None,
            "pressure": None,
            "rain_accum": None,
            "rain_duration": None,
            "rain_intensity": None,
            "heating_temp": None,
            "voltage_supply": None,
        }

        for part in data_parts:
            if '=' in part:
                key, raw_value = part.split('=')
                key = key.strip()
                raw_value = raw_value.strip()
                value = raw_value.replace('#', '') \
                                 .replace('C', '').replace('P', '').replace('B', '') \
                                 .replace('M', '').replace('N', '').replace('s', '') \
                                 .replace('V', '').replace('D', '').replace(',', '.')

                try:
                    match key:
                        case 'Dn': data_dict['wind_dir_min'] = int(value)
                        case 'Dm': data_dict['wind_dir_avg'] = int(value)
                        case 'Dx': data_dict['wind_dir_max'] = int(value)
                        case 'Sn': data_dict['wind_speed_min'] = float(value)
                        case 'Sm': data_dict['wind_speed_avg'] = float(value)
                        case 'Sx': data_dict['wind_speed_max'] = float(value)
                        case 'Ta': data_dict['temp_air'] = float(value)
                        case 'Tp': data_dict['temp_probe'] = float(value)
                        case 'Ua': data_dict['humidity'] = float(value)
                        case 'Pa': data_dict['pressure'] = float(value) * 1000  # bar to Pa
                        case 'Rc': data_dict['rain_accum'] = float(value)
                        case 'Rd': data_dict['rain_duration'] = float(value)
                        case 'Ri': data_dict['rain_intensity'] = float(value)
                        case 'Th': data_dict['heating_temp'] = float(value)
                        case 'Vs': data_dict['voltage_supply'] = float(value)
                except ValueError:
                    print(f"[⚠️] Invalid number format for key {key}: {value}")

        return data_dict
    except Exception as e:
        print(f"[ERROR] Failed to parse line: {e}")
        return {}
