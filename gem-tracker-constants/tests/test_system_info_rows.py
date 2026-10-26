import pandas as pd

from gem_tracker_constants import drop_system_info_rows, is_system_info_row


def test_drops_info_rows_keeps_route_rows():
    df = pd.DataFrame({
        "ProjectID": ["P1", "P2", "P3", "P4", "P5"],
        "SegmentName": ["SYSTEM/NETWORK INFO", "SYSTEM/NETWORK INFO (Main Line)",
                        " system/network info ", "SYSTEM/NETWORK ROUTE", "Mainline"],
    })
    assert is_system_info_row(df).tolist() == [True, True, True, False, False]
    assert drop_system_info_rows(df)["ProjectID"].tolist() == ["P4", "P5"]


def test_missing_segment_column_drops_nothing():
    df = pd.DataFrame({"ProjectID": ["P1"]})
    assert len(drop_system_info_rows(df)) == 1
