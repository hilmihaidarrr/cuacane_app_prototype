from cuacane_app.utils.line_parser import parse_0R0_line

def test_parse_line_complete():
    line = "0R0,Dn=255#,Dm=331#,Dx=065#,Sn=0.1#,Ta=25.0C"
    result = parse_0R0_line(line)
    assert result['Dn'] == '255'
    assert result['Sn'] == '0.1'
    assert result['Ta'] == '25.0C'

def test_parse_line_missing_fields():
    line = "0R0,Sn=0.1#,Ta=25.0C"
    result = parse_0R0_line(line)
    assert 'Dn' not in result
    assert result['Sn'] == '0.1'

def test_parse_line_invalid_format():
    line = "this is not sensor data"
    result = parse_0R0_line(line)
    assert isinstance(result, dict)
    assert len(result) == 0

if __name__ == "__main__":
    test_parse_line_complete()
    test_parse_line_missing_fields()
    test_parse_line_invalid_format()
    print("✅ Semua test parser sensor berhasil!")