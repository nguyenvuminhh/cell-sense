from server.middleware import BadRequestError
from server.utils import extract_sheet_name_and_range


def test_extract_sheet_name_and_range_valid():
    valid_inputs = [
        ("Sheet1!A1", ("Sheet1", "A1")),
        ("Sheet1!A1:B5", ("Sheet1", "A1:B5")),
        ("Data!Z10:Z20", ("Data", "Z10:Z20")),
        ("'My Sheet'!A1", ("My Sheet", "A1")),
        ("'Data 2025'!A1:B10", ("Data 2025", "A1:B10")),
        ("'Budget Q1'!C3:D12", ("Budget Q1", "C3:D12")),
        ("'Sheet-Name_123'!A5", ("Sheet-Name_123", "A5")),
        ("'Sales Data'!A1:AA20", ("Sales Data", "A1:AA20")),
        ("'Long Sheet Name'!Z1:Z10", ("Long Sheet Name", "Z1:Z10")),
        ("Finance!B2:C3", ("Finance", "B2:C3")),
        ("Inventory!X1", ("Inventory", "X1")),
        ("'2024 Summary'!AA10", ("2024 Summary", "AA10")),
        ("'Q4 Results'!C7:D8", ("Q4 Results", "C7:D8")),
        ("'Data_Export'!A100:B200", ("Data_Export", "A100:B200")),
        ("Sheet1!Z99", ("Sheet1", "Z99")),
        ("'MySheet'!A1", ("MySheet", "A1")),
        ("'Revenue-Data'!AA1:AA50", ("Revenue-Data", "AA1:AA50")),
        ("'Budget2025'!C10:D20", ("Budget2025", "C10:D20")),
        ("Report!A1:B2", ("Report", "A1:B2")),
        ("'Employee Records'!E5:E9", ("Employee Records", "E5:E9")),
    ]
    results = []
    for text, expected in valid_inputs:
        results.append((text, extract_sheet_name_and_range(text) == expected))
    assert all(
        valid for _, valid in results
    ), f"Failed valid cases: {[(text, valid) for text, valid in results if not valid]}"


def test_extract_sheet_name_and_range_invalid():
    invalid_inputs = [
        "",  # empty
        "A1",  # no sheet name
        "Sheet1!",  # missing range
        "Sheet1!A",  # incomplete reference
        "Sheet1!1A",  # wrong order
        "Sheet1!A0",  # invalid row
        "Sheet1!A1:B",  # invalid range end
        "Sheet1!A1:B C3",  # invalid space
        "'Sheet1!A1",  # missing closing quote
        "'Sheet1''!A1",  # extra quote
        "!!A1",  # stray exclamation
        "Sheet1!A1: B3",  # space after colon
        "Sheet1!A1 :B3",  # space before colon
        "Sheet1!A-1",  # invalid row
        "Sheet1!A01",  # leading zero
        "Sheet1!A1:B0",  # invalid row 0 in range
        "Sheet1!AA",  # missing row
        "'Unclosed!A1:B5",  # unbalanced quote
    ]

    results = []
    for text in invalid_inputs:
        try:
            extract_sheet_name_and_range(text)
            results.append((text, False))  # Should not reach here
        except BadRequestError:
            results.append((text, True))  # Expected exception

    assert all(
        invalid for _, invalid in results
    ), f"Failed invalid cases: {[(text, invalid) for text, invalid in results if not invalid]}"
