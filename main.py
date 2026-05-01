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
    invalid_barcodes = barcodes[barcodes.duplicated(subset=["barcode"], keep=False)]

    barcodes = barcodes.drop_duplicates(subset=["barcode"], keep="first")

    # Remove rows with empty order_id (unused barcodes handled separately)
    valid_barcodes = barcodes.dropna(subset=["order_id"])

    # Orders without barcodes
    orders_with_barcodes = valid_barcodes["order_id"].unique()
    invalid_orders = orders[~orders["order_id"].isin(orders_with_barcodes)]

    valid_orders = orders[orders["order_id"].isin(orders_with_barcodes)]

    return valid_orders, valid_barcodes, invalid_orders, invalid_barcodes


def get_top_five_customers(df: pd.DataFrame) -> dict:
    exploded = df.explode("barcodes")
    counts = exploded.groupby("customer_id")["barcodes"].count()
    top5 = counts.sort_values(ascending=False).head(5)

    return top5



def count_unused(barcodes: pd.DataFrame) -> int:
    return barcodes[barcodes["order_id"].isna()].shape[0]


def main():
    parser = argparse.ArgumentParser(description="Process orders and barcodes")
    parser.add_argument("orders")
    parser.add_argument("barcodes")
    parser.add_argument("-o", "--output", default="output.csv")
    args = parser.parse_args()

    orders, barcodes = load_data(args.orders, args.barcodes)
    print ("****************************")
    print("Processing Data!!")

    valid_orders, valid_barcodes, invalid_orders, invalid_barcodes = validate(orders, barcodes)

    # log invalid barcodes
    if not invalid_barcodes.empty:
        for b in invalid_barcodes["barcode"].unique():
            log_err(f"Duplicate barcode ignored: {b}")
    # log invalid orders
    if not invalid_orders.empty:
        for oid in invalid_orders["order_id"]:
            log_err(f"Order without barcodes ignored: {oid}")

    output_df = build_output(valid_orders, valid_barcodes)
    output_df.to_csv(args.output, index=False)
    top_five = get_top_five_customers(output_df)

    print ("****************************")

    print ("Top five Customers:")
    for cid, count in top_five.items():
        print(f"{cid}, {count}")
    print ("****************************")

if __name__ == "__main__":
    main()