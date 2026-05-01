import argparse
import pandas as pd
from typing import Tuple
import sys
import json

def log_err(msg: str):
    print(msg, file=sys.stderr)

def build_output(orders: pd.DataFrame, barcodes: pd.DataFrame) -> pd.DataFrame:
    used = barcodes.dropna(subset=["order_id"])

    grouped = used.groupby("order_id")["barcode"].apply(list).reset_index()
    merged = pd.merge(orders, grouped, on="order_id", how="inner")
    out = merged[["customer_id", "order_id", "barcode"]].copy()
    out.rename(columns={"barcode": "barcodes"}, inplace=True)
    return out


def load_data(orders_path: str, barcodes_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    orders = pd.read_csv(orders_path, dtype={"order_id": str, "customer_id": str})
    barcodes = pd.read_csv(barcodes_path, dtype={"barcodes": str, "order_id": str})
    return orders, barcodes


def validate(orders: pd.DataFrame, barcodes: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Remove duplicate barcodes
    dup_barcodes = barcodes[barcodes.duplicated(subset=["barcode"], keep=False)]
    if not dup_barcodes.empty:
        for b in dup_barcodes["barcode"].unique():
            log_err(f"Duplicate barcode ignored: {b}")
        barcodes = barcodes.drop_duplicates(subset=["barcode"], keep="first")

    # Remove rows with empty order_id (unused barcodes handled separately)
    valid_barcodes = barcodes.dropna(subset=["order_id"])

    # Orders without barcodes
    orders_with_barcodes = valid_barcodes["order_id"].unique()
    invalid_orders = orders[~orders["order_id"].isin(orders_with_barcodes)]
    if not invalid_orders.empty:
        for oid in invalid_orders["order_id"]:
            log_err(f"Order without barcodes ignored: {oid}")
    valid_orders = orders[orders["order_id"].isin(orders_with_barcodes)]

    return valid_orders, barcodes



def save_output(df: pd.DataFrame, path: str):
    out = df.copy()
    out["barcodes"] = out["barcodes"].apply(json.dumps)
    out.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser(description="Process orders and barcodes")
    parser.add_argument("orders")
    parser.add_argument("barcodes")
    parser.add_argument("-o", "--output", default="output.csv")
    args = parser.parse_args()

    orders, barcodes = load_data(args.orders, args.barcodes)
    valid_orders, valid_barcodes = validate(orders, barcodes)

    output_df = build_output(valid_orders, valid_barcodes)
    save_output(output_df, args.output)


if __name__ == "__main__":
    main()