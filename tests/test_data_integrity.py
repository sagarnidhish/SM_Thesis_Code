from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree

import pandas as pd
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]


def test_flat_plate_source_is_authoritative_table():
    path = ROOT / "data/source/flat_plate_literature_compiled.xlsx"
    book = pd.ExcelFile(path)
    assert book.sheet_names == ["literature_compiled_data"]
    frame = pd.read_excel(path)
    assert list(frame.columns) == ["reynolds_number", "nusselt_number"]
    assert len(frame) == 102
    assert frame.iloc[0].tolist() == [126888.931780001, 209.098000004371]
    assert frame.iloc[-1].tolist() == [2031609.42609471, 3727.92842101269]


def test_sphere_source_is_authoritative_table():
    path = ROOT / "data/source/sphere_literature_compiled.xlsx"
    book = pd.ExcelFile(path)
    assert book.sheet_names == ["literature_compiled_data"]
    frame = pd.read_excel(path)
    assert list(frame.columns) == ["reynolds_number", "nusselt_number"]
    assert len(frame) == 282
    assert frame.iloc[0].tolist() == [1.0, 2.357252475160029]
    assert frame.iloc[-1].tolist() == [300394.764315561, 718.694090615008]


def test_validation_reports_but_does_not_modify_known_quirks():
    from sm_thesis_code.data import load_dataset, validate_dataset

    flat = load_dataset(ROOT / "data/source/flat_plate_literature_compiled.xlsx")
    sphere = load_dataset(ROOT / "data/source/sphere_literature_compiled.xlsx")
    assert validate_dataset(flat) == ["1 duplicate Reynolds-number row(s)"]
    assert validate_dataset(sphere) == [
        "9 duplicate Reynolds-number row(s)",
        "9 decrease(s) in original Reynolds-number row order",
    ]
    assert len(flat) == 102
    assert len(sphere) == 282


def test_workbook_metadata_is_neutral():
    for name in ["flat_plate_literature_compiled.xlsx", "sphere_literature_compiled.xlsx"]:
        workbook = load_workbook(ROOT / "data/source" / name)
        sheet = workbook["literature_compiled_data"]
        expected = "SM Thesis Code contributors"
        assert workbook.properties.creator == expected
        assert workbook.properties.lastModifiedBy == expected
        assert sheet["A1"].comment.author == expected
        assert sheet["B1"].comment.author == expected


def test_table_filter_does_not_overlap_a_worksheet_filter():
    namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    for name in ["flat_plate_literature_compiled.xlsx", "sphere_literature_compiled.xlsx"]:
        with ZipFile(ROOT / "data/source" / name) as archive:
            worksheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
            table = ElementTree.fromstring(archive.read("xl/tables/table1.xml"))
        assert worksheet.find("x:autoFilter", namespace) is None
        assert table.find("x:autoFilter", namespace) is not None
