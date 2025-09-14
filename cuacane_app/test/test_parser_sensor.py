from cuacane_app.utils.line_parser import parse_0R0_line
import math

def test_parse_line_complete():
    line = "0R0,Dn=255#,Dm=331#,Dx=065#,Sn=0.1#,Sm=0.9#,Sx=1.4#,Ta=25.0C,Tp=25.3C,Ua=70.2P,Pa=0.9248B,Rc=0.0M,Rd=0s,Ri=0.0M,Th=23.4C,Vs=12.0N"
    result = parse_0R0_line(line)
    assert result['wind_dir_min'] == 255
    assert result['wind_dir_avg'] == 331
    assert result['wind_dir_max'] == 65
    assert result['wind_speed_min'] == 0.1
    assert result['wind_speed_avg'] == 0.9
    assert result['wind_speed_max'] == 1.4
    assert result['temp_air'] == 25.0
    assert result['temp_probe'] == 25.3
    assert result['humidity'] == 70.2
    assert math.isclose(result['pressure'], 924.8, rel_tol=1e-4)
    assert result['rain_accum'] == 0.0
    assert result['rain_duration'] == 0.0
    assert result['rain_intensity'] == 0.0
    assert result['heating_temp'] == 23.4
    assert result['voltage_supply'] == 12.0

def test_parse_line_missing_fields():
    line = "0R0,Sn=0.1#,Ta=25.0C"
    result = parse_0R0_line(line)
    assert result['wind_speed_min'] == 0.1
    assert result['temp_air'] == 25.0
    assert result['wind_dir_min'] is None
    assert result['pressure'] is None
    assert result['rain_accum'] is None

def test_parse_line_invalid_format():
    line = "this is not a valid sensor line"
    result = parse_0R0_line(line)
    assert isinstance(result, dict)
    assert all(k == 'datetime' or v is None for k, v in result.items())

def test_parse_line_weird_values():
    line = "0R0,Dn=???,Dm=-999#,Sn=#,Ta=abcC"
    result = parse_0R0_line(line)
    assert result['wind_dir_min'] is None
    assert result['wind_dir_avg'] == -999
    assert result['wind_speed_min'] is None
    assert result['temp_air'] is None

def test_parse_line_extra_spaces():
    line = "0R0,  Dn = 123# , Ta= 30.0C , Pa=1.002B  "
    result = parse_0R0_line(line)
    assert result['wind_dir_min'] == 123
    assert result['temp_air'] == 30.0
    assert math.isclose(result['pressure'], 1002.0, rel_tol=1e-5)

def test_parse_line_different_order():
    line = "0R0,Pa=0.990B,Ta=27.0C,Dn=220#,Sn=0.5#"
    result = parse_0R0_line(line)
    assert math.isclose(result['pressure'], 990.0, rel_tol=1e-5)
    assert result['temp_air'] == 27.0
    assert result['wind_dir_min'] == 220
    assert result['wind_speed_min'] == 0.5

def test_parse_line_partial_numeric():
    line = "0R0,Ta=25C,Ua=70P"
    result = parse_0R0_line(line)
    assert result['temp_air'] == 25.0
    assert result['humidity'] == 70.0

def test_parse_line_empty():
    line = ""
    result = parse_0R0_line(line)
    assert isinstance(result, dict)
    assert all(k == 'datetime' or v is None for k, v in result.items())

if __name__ == "__main__":
    test_parse_line_complete()
    test_parse_line_missing_fields()
    test_parse_line_invalid_format()
    test_parse_line_weird_values()
    test_parse_line_extra_spaces()
    test_parse_line_different_order()
    test_parse_line_partial_numeric()
    test_parse_line_empty()
    print("✅ Semua test parser sensor berhasil!")
