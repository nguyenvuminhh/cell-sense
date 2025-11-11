from server.utils import extract_target_cell


def test_extract_target_cell_valid():
    valid_messages = [
        "<target>Hello world</target>",
        "Prefix <target>cellA1</target> suffix",
        "<target>  value123  </target>",
        "<target>Line1\nLine2</target>",
        "<target>Text with < and > symbols</target>",
        "<target>range: A1:B2</target>",
        "<target>multiple words inside target</target>",
        "Some text <target>42</target> more text",
        "<target>\n  spaced text\n</target>",
        "<target>special chars !@#$%^&*</target>",
        "<target>Mix of numbers 123 and text</target>",
        "<target>Multi-line\ncontent\ninside</target>",
        "before <target> something </target> after",
        "<target>abc</target><target>def</target>",
        "<target>1</target><target>2</target><target>3</target>",
        "foo <target>bar</target> baz <target>qux</target>",
        "<target>123</target> and <target>456</target>",
        "nested but valid outer <target>inner value</target>",
        "<target>UPPERCASE CONTENT</target>",
        "<target>Final valid message!</target>",
    ]
    results = []
    for msg in valid_messages:
        result = extract_target_cell(msg)
        results.append((msg, len(result) > 0))
    assert all(
        valid for _, valid in results
    ), f"Failed valid cases: {[(msg) for msg, valid in results if not valid]}"


def test_extract_target_cell_invalid():

    invalid_messages = [
        "no target tags here",
        "<target>missing closing tag",
        "missing opening tag</target>",
        "<target></target",  # missing '>'
        "<target>unclosed inner <target>test</target",
        "<targt>misspelled tag</targt>",
        "<target value='oops'>not allowed syntax</target>",
        "< target>space after bracket</target>",
        "<target>missing end tag completely",
        "<target incomplete>",
        "<target/> self-closing not valid here",
        "<target><target>nested start only</targetX>",
        "<target>no closing tag <target>again</targetX>",
        "random text with <trgt>bad tag</trgt>",
        "completely malformed <target invalid>",
        "<target invalid content</target>",
        "<<target>>double open symbols",
        "<<<target>double malformed",
        "<target something>stray attributes</targetX>",
    ]
    results = []

    for msg in invalid_messages:
        result = extract_target_cell(msg)
        results.append((msg, len(result) == 0))
    assert all(
        invalid for _, invalid in results
    ), f"Failed invalid cases: {[(msg) for msg, invalid in results if not invalid]}"
