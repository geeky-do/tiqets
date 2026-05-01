import argparse
import pandas as pd
from typing import Tuple

def build_output(orders: pd.DataFrame, barcodes: pd.DataFrame) -> pd.DataFrame:
    used = barcodes.dropna(subset=["order_id"])

    grouped = used.groupby("order_id")["barcode"].apply(list).reset_index()
    merged = pd.merge(orders, grouped, on="order_id", how="inner")

    return merged[["customer_id", "order_id", "barcode"]]


def load_data(orders_path: str, barcodes_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    orders = pd.read_csv(orders_path, dtype={"order_id": str, "customer_id": str})
    barcodes = pd.read_csv(barcodes_path, dtype={"barcode": str, "order_id": str})
    return orders, barcodes

def main():
    parser = argparse.ArgumentParser(description="Process orders and barcodes")
    parser.add_argument("orders")
    parser.add_argument("barcodes")
    parser.add_argument("-o", "--output", default="output.csv")
    args = parser.parse_args()

    orders, barcodes = load_data(args.orders, args.barcodes)
    output_df = build_output(orders, barcodes)
    output_df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()