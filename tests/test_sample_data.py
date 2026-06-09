import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.sample_data import generate_sample_sales_df


class TestSampleSalesData:
    def setup_method(self):
        self.df = generate_sample_sales_df()

    def test_returns_correct_shape(self):
        assert self.df.shape == (2823, 9)

    def test_returns_2823_rows(self):
        assert len(self.df) == 2823

    def test_returns_9_columns(self):
        assert len(self.df.columns) == 9

    def test_column_names_match_expected(self):
        expected_columns = {
            "Date", "Order_ID", "Customer_ID", "Region",
            "Product_Category", "Product", "Revenue", "Profit", "PostalCode",
        }
        assert set(self.df.columns) == expected_columns

    def test_column_order(self):
        expected = [
            "Date", "Order_ID", "Customer_ID", "Region",
            "Product_Category", "Product", "Revenue", "Profit", "PostalCode",
        ]
        assert list(self.df.columns) == expected

    def test_exactly_465_missing_values_in_postal_code(self):
        null_count = self.df["PostalCode"].isnull().sum()
        assert null_count == 465

    def test_no_other_columns_have_missing_values(self):
        for col in self.df.columns:
            if col == "PostalCode":
                continue
            assert self.df[col].isnull().sum() == 0, f"Column {col} has missing values"

    def test_date_column_is_datetime(self):
        assert pd.api.types.is_datetime64_any_dtype(self.df["Date"])

    def test_revenue_column_is_numeric(self):
        assert pd.api.types.is_numeric_dtype(self.df["Revenue"])

    def test_profit_column_is_numeric(self):
        assert pd.api.types.is_numeric_dtype(self.df["Profit"])

    def test_region_contains_expected_values(self):
        expected_regions = {"EMEA", "APAC", "Japan"}
        assert expected_regions.issuperset(self.df["Region"].unique())

    def test_product_category_contains_expected_values(self):
        expected = {
            "Classic Cars", "Vintage Cars", "Motorcycles",
            "Trucks and Buses", "Planes", "Ships", "Trains",
        }
        assert expected.issuperset(self.df["Product_Category"].unique())

    def test_data_is_sorted_by_date(self):
        dates = self.df["Date"]
        assert dates.is_monotonic_increasing

    def test_deterministic_with_seed(self):
        df1 = generate_sample_sales_df(n_rows=100)
        df2 = generate_sample_sales_df(n_rows=100)
        pd.testing.assert_frame_equal(df1, df2)

    def test_no_negative_revenue(self):
        assert (self.df["Revenue"] >= 0).all()

    def test_no_negative_profit(self):
        assert (self.df["Profit"] >= 0).all()

    def test_postal_code_is_string(self):
        non_null = self.df["PostalCode"].dropna()
        assert non_null.apply(isinstance, args=(str,)).all()
