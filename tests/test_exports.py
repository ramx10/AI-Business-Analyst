import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from utils.exports import (
    export_to_csv,
    export_to_excel,
    export_to_parquet,
    export_to_json,
    export_to_tableau_hyper,
    export_to_tableau_tde,
    export_to_powerbi,
    export_to_google_sheets,
    get_export_formats,
)


SAMPLE_DF = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "revenue": [100.0, 200.0, 300.0],
    "category": ["A", "B", "A"],
})

SAMPLE_INT_DF = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "revenue": [100, 200, 300],
    "category": ["A", "B", "A"],
})


class TestExportToCSV:
    def test_writes_valid_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_to_csv(SAMPLE_DF, path)
            result = pd.read_csv(path)
            pd.testing.assert_frame_equal(result, SAMPLE_DF)
        finally:
            os.remove(path)

    def test_content_matches(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_to_csv(SAMPLE_DF, path)
            with open(path) as fh:
                content = fh.read()
            assert "Alice" in content
            assert "revenue" in content
        finally:
            os.remove(path)


class TestExportToExcel:
    def test_writes_valid_excel(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            export_to_excel(SAMPLE_INT_DF, path)
            result = pd.read_excel(path, engine="openpyxl")
            result["revenue"] = result["revenue"].astype(int)
            pd.testing.assert_frame_equal(result, SAMPLE_INT_DF)
        finally:
            os.remove(path)

    def test_custom_sheet_name(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            export_to_excel(SAMPLE_DF, path, sheet_name="CustomSheet")
            with pd.ExcelFile(path, engine="openpyxl") as xl:
                assert "CustomSheet" in xl.sheet_names
        finally:
            if os.path.exists(path):
                os.remove(path)


class TestExportToParquet:
    def test_writes_valid_parquet(self):
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            path = f.name
        try:
            export_to_parquet(SAMPLE_DF, path)
            result = pd.read_parquet(path)
            pd.testing.assert_frame_equal(result, SAMPLE_DF)
        finally:
            os.remove(path)


class TestExportToJSON:
    def test_writes_valid_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(SAMPLE_DF, path)
            with open(path) as fh:
                data = json.load(fh)
            assert len(data) == 3
            assert data[0]["name"] == "Alice"
        finally:
            os.remove(path)

    def test_records_orient_by_default(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(SAMPLE_DF, path)
            with open(path) as fh:
                data = json.load(fh)
            assert isinstance(data, list)
        finally:
            os.remove(path)

    def test_custom_orient(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(SAMPLE_DF, path, orient="split")
            with open(path) as fh:
                data = json.load(fh)
            assert "data" in data
            assert "columns" in data
        finally:
            os.remove(path)

    def test_content_matches(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(SAMPLE_INT_DF, path)
            result = pd.read_json(path, orient="records")
            result["revenue"] = result["revenue"].astype(int)
            pd.testing.assert_frame_equal(result, SAMPLE_INT_DF)
        finally:
            os.remove(path)


class TestExportToTableauHyper:
    def test_calls_pantab_frame_to_hyper(self):
        import sys
        mock_pantab = MagicMock()
        sys.modules["pantab"] = mock_pantab
        try:
            with tempfile.NamedTemporaryFile(suffix=".hyper", delete=False) as f:
                path = f.name
            try:
                export_to_tableau_hyper(SAMPLE_DF, path)
                mock_pantab.frame_to_hyper.assert_called_once_with(SAMPLE_DF, path, table="export")
            finally:
                os.remove(path)
        finally:
            sys.modules.pop("pantab", None)


class TestExportToTableauTDE:
    def test_converts_to_hyper_instead(self):
        import sys
        mock_pantab = MagicMock()
        sys.modules["pantab"] = mock_pantab
        try:
            with tempfile.NamedTemporaryFile(suffix=".tde", delete=False) as f:
                path = f.name
            try:
                export_to_tableau_tde(SAMPLE_DF, path)
                expected = path.replace(".tde", ".hyper")
                mock_pantab.frame_to_hyper.assert_called_once_with(SAMPLE_DF, expected, table="export")
            finally:
                if os.path.exists(path):
                    os.remove(path)
        finally:
            sys.modules.pop("pantab", None)


class TestExportToPowerBI:
    def test_delegates_to_parquet(self):
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            path = f.name
        try:
            export_to_powerbi(SAMPLE_DF, path)
            result = pd.read_parquet(path)
            pd.testing.assert_frame_equal(result, SAMPLE_DF)
        finally:
            os.remove(path)


class TestExportToGoogleSheets:
    def _setup_gs_mocks(self):
        import sys
        mock_gspread = MagicMock()
        mock_creds_cls = MagicMock()
        sys.modules["gspread"] = mock_gspread
        sys.modules["oauth2client"] = MagicMock()
        sys.modules["oauth2client.service_account"] = MagicMock()
        sys.modules["oauth2client.service_account"].ServiceAccountCredentials = mock_creds_cls
        return mock_creds_cls, mock_gspread

    def _teardown_gs_mocks(self):
        import sys
        sys.modules.pop("gspread", None)
        sys.modules.pop("oauth2client", None)
        sys.modules.pop("oauth2client.service_account", None)

    def test_updates_worksheet(self):
        mock_creds_cls, mock_gspread = self._setup_gs_mocks()
        try:
            mock_creds = MagicMock()
            mock_creds_cls.from_json_keyfile_dict.return_value = mock_creds
            mock_client = MagicMock()
            mock_gspread.authorize.return_value = mock_client
            mock_sheet = MagicMock()
            mock_client.open_by_key.return_value = mock_sheet
            mock_worksheet = MagicMock()
            mock_sheet.worksheet.return_value = mock_worksheet

            credentials_json = json.dumps({"type": "service_account", "project_id": "test"})
            export_to_google_sheets(SAMPLE_DF, credentials_json, "test-spreadsheet", "Export")

            mock_creds_cls.from_json_keyfile_dict.assert_called_once()
            mock_gspread.authorize.assert_called_once_with(mock_creds)
            mock_client.open_by_key.assert_called_once_with("test-spreadsheet")
            mock_sheet.worksheet.assert_called_once_with("Export")
            args, _ = mock_worksheet.update.call_args
            assert len(args[0]) == 4
        finally:
            self._teardown_gs_mocks()

    def test_creates_missing_worksheet(self):
        mock_creds_cls, mock_gspread = self._setup_gs_mocks()
        try:
            mock_creds = MagicMock()
            mock_creds_cls.from_json_keyfile_dict.return_value = mock_creds
            mock_client = MagicMock()
            mock_gspread.authorize.return_value = mock_client
            mock_sheet = MagicMock()
            mock_client.open_by_key.return_value = mock_sheet
            mock_sheet.worksheet.side_effect = Exception("not found")

            credentials_json = json.dumps({"type": "service_account", "project_id": "test"})
            export_to_google_sheets(SAMPLE_DF, credentials_json, "test-spreadsheet", "NewSheet")

            mock_sheet.add_worksheet.assert_called_once_with(title="NewSheet", rows="1000", cols="26")
        finally:
            self._teardown_gs_mocks()


class TestGetExportFormats:
    def test_returns_list(self):
        formats = get_export_formats()
        assert isinstance(formats, list)

    def test_contains_expected_formats(self):
        formats = get_export_formats()
        ids = [f["id"] for f in formats]
        expected = {"csv", "excel", "parquet", "json", "tableau_hyper", "powerbi", "google_sheets"}
        assert expected.issubset(set(ids))

    def test_each_format_has_required_keys(self):
        formats = get_export_formats()
        for fmt in formats:
            assert "id" in fmt
            assert "name" in fmt
            assert "icon" in fmt
            assert "description" in fmt
            assert "extension" in fmt

    def test_csv_has_csv_extension(self):
        formats = get_export_formats()
        csv_fmt = next(f for f in formats if f["id"] == "csv")
        assert csv_fmt["extension"] == ".csv"

    def test_excel_has_xlsx_extension(self):
        formats = get_export_formats()
        excel_fmt = next(f for f in formats if f["id"] == "excel")
        assert excel_fmt["extension"] == ".xlsx"


class TestRoundTripDataIntegrity:
    def test_csv_round_trip(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_to_csv(SAMPLE_DF, path)
            result = pd.read_csv(path)
            assert result["revenue"].tolist() == [100.0, 200.0, 300.0]
        finally:
            os.remove(path)

    def test_excel_round_trip(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            export_to_excel(SAMPLE_INT_DF, path)
            result = pd.read_excel(path, engine="openpyxl")
            assert result["name"].tolist() == ["Alice", "Bob", "Charlie"]
            assert result["revenue"].tolist() == [100, 200, 300]
        finally:
            os.remove(path)

    def test_parquet_round_trip(self):
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            path = f.name
        try:
            export_to_parquet(SAMPLE_DF, path)
            result = pd.read_parquet(path)
            assert result["revenue"].sum() == 600.0
        finally:
            os.remove(path)

    def test_json_round_trip(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(SAMPLE_DF, path)
            result = pd.read_json(path, orient="records")
            assert len(result) == 3
        finally:
            os.remove(path)


class TestEdgeCases:
    def test_empty_dataframe_csv(self):
        df = pd.DataFrame()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            export_to_csv(df, path)
            with open(path) as fh:
                content = fh.read()
            assert content == "" or content == "\r\n" or content.strip() == ""
        finally:
            os.remove(path)

    def test_single_column_dataframe_json(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            export_to_json(df, path)
            with open(path) as fh:
                data = json.load(fh)
            assert len(data) == 3
            assert data[0]["x"] == 1
        finally:
            os.remove(path)

    def test_dataframe_with_nulls_parquet(self):
        df = pd.DataFrame({"a": [1, None, 3], "b": ["x", None, "z"]})
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            path = f.name
        try:
            export_to_parquet(df, path)
            result = pd.read_parquet(path)
            assert result["a"].isnull().sum() == 1
            assert result["b"].isnull().sum() == 1
        finally:
            os.remove(path)
