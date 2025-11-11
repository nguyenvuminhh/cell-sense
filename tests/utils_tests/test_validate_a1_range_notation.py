from server.utils import validate_a1_range_notation


def test_extract_target_cell_valid():
    valid_messages = [
        "A1",
        "B2",
        "AA10",
        "Z999",
        "A1:B2",
        "C3:D4",
        "Sheet1!A1",
        "Sheet1!A1:B5",
        "Data!Z10:Z20",
        "'My Sheet'!A1",
        "'Data 2025'!A1:B10",
        "'Budget Q1'!C3:D12",
        "'Sheet-Name_123'!A5",
        "'Sales Data'!A1:AA20",
        "'Long Sheet Name'!Z1:Z10",
        "Finance!B2:C3",
        "Inventory!X1",
        "'2024 Summary'!AA10",
        "'Q4 Results'!C7:D8",
        "'Data_Export'!A100:B200",
    ]
    results = []
    for msg in valid_messages:
        results.append((msg, validate_a1_range_notation(msg)))
    assert all(
        valid for _, valid in results
    ), f"Failed valid cases: {[(text) for text, valid in results if not valid]}"


def test_extract_target_cell_invalid():
    invalid_messages = [
        "",  # empty
        "A0",  # row 0 invalid
        "1A",  # wrong order
        "Sheet1!A",  # missing row
        "A1:B",  # missing second row
        "Sheet!A1:B",  # incomplete range
        "A:B",  # missing rows
        "AA",  # missing row number
        "Sheet!1A",  # bad order
        "Sheet!A1:B C3",  # space inside range
        "Sheet!A1: B3",  # space after colon
        "Sheet!A1 :B3",  # space before colon
        "Sheet!A1:B3 ",  # trailing space
        " Sheet!A1:B3",  # leading space
        "'My Sheet!A1",  # missing closing quote
        "'My Sheet''!A1",  # extra quote
        "Sheet1!A-1",  # invalid char in row
        "Sheet1!A1:B0",  # invalid second row
        "Sheet1!A01",  # leading zero
        "!!A1",  # stray exclamation
    ]

    results = []
    for msg in invalid_messages:
        results.append((msg, not validate_a1_range_notation(msg)))
    assert all(
        invalid for _, invalid in results
    ), f"Failed invalid cases: {[(text) for text, invalid in results if not invalid]}"
