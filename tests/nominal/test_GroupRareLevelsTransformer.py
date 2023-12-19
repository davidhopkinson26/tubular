import numpy as np
import pandas as pd
import pytest
import test_aide as ta

import tests.test_data as d
import tubular
from tubular.nominal import GroupRareLevelsTransformer


class TestInit:
    """Tests for GroupRareLevelsTransformer.init()."""

    def test_super_init_called(self, mocker):
        """Test that init calls BaseTransformer.init."""
        expected_call_args = {
            0: {"args": (), "kwargs": {"columns": None, "verbose": True, "copy": True}},
        }

        with ta.functions.assert_function_call(
            mocker,
            tubular.base.BaseTransformer,
            "__init__",
            expected_call_args,
        ):
            GroupRareLevelsTransformer(columns=None, verbose=True, copy=True)

    def test_cut_off_percent_not_float_error(self):
        """Test that an exception is raised if cut_off_percent is not an float."""
        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: cut_off_percent must be a float",
        ):
            GroupRareLevelsTransformer(cut_off_percent="a")

    def test_cut_off_percent_negative_error(self):
        """Test that an exception is raised if cut_off_percent is negative."""
        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: cut_off_percent must be > 0 and < 1",
        ):
            GroupRareLevelsTransformer(cut_off_percent=-1.0)

    def test_cut_off_percent_gt_one_error(self):
        """Test that an exception is raised if cut_off_percent is greater than 1."""
        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: cut_off_percent must be > 0 and < 1",
        ):
            GroupRareLevelsTransformer(cut_off_percent=2.0)

    def test_weight_not_str_error(self):
        """Test that an exception is raised if weight is not a str, if supplied."""
        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: weight should be a single column",
        ):
            GroupRareLevelsTransformer(weight=2)

    def test_record_rare_levels_not_bool_error(self):
        """Test that an exception is raised if record_rare_levels is not a bool."""
        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: record_rare_levels must be a bool",
        ):
            GroupRareLevelsTransformer(record_rare_levels=2)

    def test_encode_unseen_levels_not_bool_error(self):
        """Test that an exception is raised if encode_unseen_levels is not a bool."""
        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: encode_unseen_levels must be a bool",
        ):
            GroupRareLevelsTransformer(encode_unseen_levels=2)


class TestFit:
    """Tests for GroupRareLevelsTransformer.fit()."""

    def test_super_fit_called(self, mocker):
        """Test that fit calls BaseTransformer.fit."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"])

        expected_call_args = {0: {"args": (d.create_df_5(), None), "kwargs": {}}}

        with ta.functions.assert_function_call(
            mocker,
            tubular.base.BaseTransformer,
            "fit",
            expected_call_args,
        ):
            x.fit(df)

    def test_weight_column_not_in_X_error(self):
        """Test that an exception is raised if weight is not in X."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"], weight="aaaa")

        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: weight aaaa not in X",
        ):
            x.fit(df)

    def test_fit_returns_self(self):
        """Test fit returns self?."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"])

        x_fitted = x.fit(df)

        assert (
            x_fitted is x
        ), "Returned value from GroupRareLevelsTransformer.fit not as expected."

    def test_fit_not_changing_data(self):
        """Test fit does not change X."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"])

        x.fit(df)

        ta.equality.assert_equal_dispatch(
            expected=d.create_df_5(),
            actual=df,
            msg="Check X not changing during fit",
        )

    def test_learnt_values_no_weight(self):
        """Test that the impute values learnt during fit, without using a weight, are expected."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"], cut_off_percent=0.2)

        x.fit(df)

        ta.classes.test_object_attributes(
            obj=x,
            expected_attributes={
                "mapping_": {"b": ["a", np.NaN], "c": ["a", "c", "e"]},
            },
            msg="mapping_ attribute",
        )

    def test_learnt_values_weight(self):
        """Test that the impute values learnt during fit, using a weight, are expected."""
        df = d.create_df_6()

        x = GroupRareLevelsTransformer(columns=["b"], cut_off_percent=0.3, weight="a")

        x.fit(df)

        ta.classes.test_object_attributes(
            obj=x,
            expected_attributes={"mapping_": {"b": ["a", np.NaN]}},
            msg="mapping_ attribute",
        )

    def test_learnt_values_weight_2(self):
        """Test that the impute values learnt during fit, using a weight, are expected."""
        df = d.create_df_6()

        x = GroupRareLevelsTransformer(columns=["c"], cut_off_percent=0.2, weight="a")

        x.fit(df)

        ta.classes.test_object_attributes(
            obj=x,
            expected_attributes={"mapping_": {"c": ["f", "g"]}},
            msg="mapping_ attribute",
        )

    def test_rare_level_name_not_diff_col_type(self):
        """Test that an exception is raised if rare_level_name is of a different type with respect columns."""
        df = d.create_df_10()

        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: rare_level_name must be of the same type of the columns",
        ):
            x = GroupRareLevelsTransformer(columns=["a", "b"], rare_level_name=2)

            x.fit(df)

        with pytest.raises(
            ValueError,
            match="GroupRareLevelsTransformer: rare_level_name must be of the same type of the columns",
        ):
            x = GroupRareLevelsTransformer(columns=["c"])

            x.fit(df)

    def test_training_data_levels_stored(self):
        """Test that the levels present in the training data are stored if encode_unseen_levels is false"""
        df = d.create_df_8()

        expected_training_data_levels = {
            "b": set(df["b"]),
            "c": set(df["c"]),
        }

        x = GroupRareLevelsTransformer(columns=["b", "c"], encode_unseen_levels=False)
        x.fit(df)
        ta.equality.assert_equal_dispatch(
            expected=expected_training_data_levels,
            actual=x.training_data_levels,
            msg="Training data values not correctly stored when encode_unseen_levels is false",
        )


class TestTransform:
    """Tests for GroupRareLevelsTransformer.transform()."""

    def expected_df_1():
        """Expected output for test_expected_output_no_weight."""
        df = pd.DataFrame({"a": [1, 2, 3, 4, 5, 6, 7, 8, 9, np.NaN]})

        df["b"] = pd.Series(
            ["a", "a", "a", "rare", "rare", "rare", "rare", np.NaN, np.NaN, np.NaN],
        )

        df["c"] = pd.Series(
            ["a", "a", "c", "c", "e", "e", "rare", "rare", "rare", "rare"],
            dtype=pd.CategoricalDtype(
                categories=["a", "c", "e", "f", "g", "h", "rare"],
                ordered=False,
            ),
        )

        return df

    def expected_df_2():
        """Expected output for test_expected_output_weight."""
        df = pd.DataFrame(
            {
                "a": [2, 2, 2, 2, np.NaN, 2, 2, 2, 3, 3],
                "b": ["a", "a", "a", "d", "e", "f", "g", np.NaN, np.NaN, np.NaN],
                "c": ["a", "b", "c", "d", "f", "f", "f", "g", "g", np.NaN],
            },
        )

        df["c"] = df["c"].astype("category")

        df["b"] = pd.Series(
            ["a", "a", "a", "rare", "rare", "rare", "rare", np.NaN, np.NaN, np.NaN],
        )

        return df

    def test_check_is_fitted_called(self, mocker):
        """Test that BaseTransformer check_is_fitted called."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"])

        x.fit(df)

        expected_call_args = {0: {"args": (["mapping_"],), "kwargs": {}}}

        with ta.functions.assert_function_call(
            mocker,
            tubular.base.BaseTransformer,
            "check_is_fitted",
            expected_call_args,
        ):
            x.transform(df)

    def test_super_transform_called(self, mocker):
        """Test that BaseTransformer.transform called."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"])

        x.fit(df)

        expected_call_args = {
            0: {
                "args": (
                    x,
                    d.create_df_5(),
                ),
                "kwargs": {},
            },
        }

        with ta.functions.assert_function_call(
            mocker,
            tubular.nominal.BaseNominalTransformer,
            "transform",
            expected_call_args,
            return_value=d.create_df_5(),
        ):
            x.transform(df)

    def test_learnt_values_not_modified(self):
        """Test that the mapping_ from fit are not changed in transform."""
        df = d.create_df_5()

        x = GroupRareLevelsTransformer(columns=["b", "c"])

        x.fit(df)

        x2 = GroupRareLevelsTransformer(columns=["b", "c"])

        x2.fit(df)

        x2.transform(df)

        ta.equality.assert_equal_dispatch(
            expected=x.mapping_,
            actual=x2.mapping_,
            msg="Non rare levels not changed in transform",
        )

    @pytest.mark.parametrize(
        ("df", "expected"),
        ta.pandas.adjusted_dataframe_params(d.create_df_5(), expected_df_1()),
    )
    def test_expected_output_no_weight(self, df, expected):
        """Test that the output is expected from transform."""
        x = GroupRareLevelsTransformer(columns=["b", "c"], cut_off_percent=0.2)

        # set the mappging dict directly rather than fitting x on df so test works with decorators
        x.mapping_ = {"b": ["a", np.NaN], "c": ["e", "c", "a"]}

        df_transformed = x.transform(df)

        ta.equality.assert_frame_equal_msg(
            actual=df_transformed,
            expected=expected,
            msg_tag="Unexpected values in GroupRareLevelsTransformer.transform",
        )

    def test_expected_output_no_weight_single_row_na(self):
        """Test output from a single row transform with np.NaN value remains the same,
        the type is perserved if using existing dataframe, so need to create a new dataframe.
        """
        one_row_df = pd.DataFrame({"b": [np.nan], "c": [np.NaN]})
        x = GroupRareLevelsTransformer(columns=["b", "c"], cut_off_percent=0.2)

        # set the mappging dict directly rather than fitting x on df so test works with decorators
        x.mapping_ = {"b": ["a", np.NaN], "c": ["e", "c", "a", np.NaN]}

        one_row_df_transformed = x.transform(one_row_df)

        ta.equality.assert_frame_equal_msg(
            actual=one_row_df_transformed,
            expected=one_row_df,
            msg_tag="Unexpected values in GroupRareLevelsTransformer.transform",
        )

    def test_expected_output_no_weight_single_row_na_category_column(self):
        """Test output from a single row transform with np.NaN value remains the same, when column is type category,
        the type is perserved if using existing dataframe, so need to create a new dataframe.
        """
        one_row_df = pd.DataFrame({"b": [np.nan], "c": [np.NaN]})
        one_row_df["c"] = one_row_df["c"].astype("category")

        # add rare as a category in dataframe
        one_row_df["c"] = one_row_df["c"].cat.add_categories("rare")

        x = GroupRareLevelsTransformer(columns=["b", "c"], cut_off_percent=0.2)

        # set the mappging dict directly rather than fitting x on df so test works with decorators
        x.mapping_ = {"b": ["a", np.NaN], "c": ["e", "c", "a", np.NaN]}

        one_row_df_transformed = x.transform(one_row_df)

        ta.equality.assert_frame_equal_msg(
            actual=one_row_df_transformed,
            expected=one_row_df,
            msg_tag="Unexpected values in GroupRareLevelsTransformer.transform",
        )

    @pytest.mark.parametrize(
        ("df", "expected"),
        ta.pandas.adjusted_dataframe_params(d.create_df_6(), expected_df_2()),
    )
    def test_expected_output_weight(self, df, expected):
        """Test that the output is expected from transform, when weights are used."""
        x = GroupRareLevelsTransformer(columns=["b"], cut_off_percent=0.3, weight="a")

        # set the mappging dict directly rather than fitting x on df so test works with decorators
        x.mapping_ = {"b": ["a", np.NaN]}

        df_transformed = x.transform(df)

        ta.equality.assert_frame_equal_msg(
            actual=df_transformed,
            expected=expected,
            msg_tag="Unexpected values in GroupRareLevelsTransformer.transform (with weights)",
        )

    @pytest.mark.parametrize(("label", "col"), [(2.0, "a"), ("zzzz", "b"), (100, "c")])
    def test_rare_level_name_same_col_type(self, label, col):
        """Test that checks if output columns are of the same type with respect to the input label."""
        df = d.create_df_10()

        x = GroupRareLevelsTransformer(columns=[col], rare_level_name=label)

        x.fit(df)

        df_2 = x.transform(df)

        assert (
            pd.Series(label).dtype == df_2[col].dtypes
        ), "column type should be the same as label type"

    def test_expected_output_unseen_levels_not_encoded(self):
        """Test that unseen levels are not encoded when encode_unseen_levels is false"""

        df = d.create_df_8()

        expected = ["w", "w", "rare", "rare", "unseen_level"]

        x = GroupRareLevelsTransformer(
            columns=["b", "c"],
            cut_off_percent=0.3,
            encode_unseen_levels=False,
        )
        x.fit(df)

        df["b"] = ["w", "w", "z", "y", "unseen_level"]

        df_transformed = x.transform(df)

        ta.equality.assert_equal_dispatch(
            expected=expected,
            actual=list(df_transformed["b"]),
            msg="Unseen levels are not left unchanged when encode_unseen_levels is set to false",
        )
