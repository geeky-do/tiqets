import argparse
import pandas as pd
from typing import Tuple
import sys

def log_err(msg: str):
    print(msg, file=sys.stderr)

def build_output(orders: pd.DataFrame, barcodes: pd.DataFrame) -> pd.DataFrame:
    """
    Construct the output dataset by combining orders with their associated barcodes.
    Args:
        orders (pd.DataFrame)
        barcodes (pd.DataFrame)

    Returns:
        pd.DataFrame:
            DataFrame with columns:
            - customer_id (str)
            - order_id (str)
            - barcodes (List[str]): List of barcodes associated with the order

    Notes:
        - Only orders with at least one barcode are included (inner join).
        - Assumes input has already been validated (e.g., duplicates handled).
    """
    used = barcodes.dropna(subset=["order_id"])

    grouped = used.groupby("order_id")["barcode"].apply(list).reset_index()
    merged = pd.merge(orders, grouped, on="order_id", how="inner")
    out = merged[["customer_id", "order_id", "barcode"]].copy()
    out.rename(columns={"barcode": "barcodes"}, inplace=True)
    return out


def load_data(orders_path: str, barcodes_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load orders and barcodes data from CSV files.

    Args:
        orders_path (str): Path to the orders CSV file.

        barcodes_path (str): Path to the barcodes CSV file.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            - orders DataFrame
            - barcodes DataFrame
    """    
    orders = pd.read_csv(orders_path, dtype={"order_id": str, "customer_id": str})
    barcodes = pd.read_csv(barcodes_path, dtype={"barcodes": str, "order_id": str})
    return orders, barcodes


def validate(orders: pd.DataFrame, barcodes: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate and clean orders and barcodes data.

    This function performs:
    - Removal of duplicate barcodes 
    - Identification of invalid orders (orders without any barcodes)

    Args:
        orders (pd.DataFrame)

        barcodes (pd.DataFrame)

    Returns:
        Tuple containing:
            valid_orders (pd.DataFrame):
                Orders that have at least one associated barcode

            barcodes (pd.DataFrame):
                Cleaned barcodes DataFrame (duplicates removed)

            invalid_orders (pd.DataFrame):
                Orders that have no associated barcodes

            dup_barcodes (pd.DataFrame):
                Rows containing duplicate barcodes that were removed

    Notes:
        - Duplicate detection is based on the 'barcode' column.
        - Barcodes without order_id are retained (used later for unused count).
        - Invalid orders are excluded from further processing but returned for logging/debugging.
    """

    # Remove duplicate barcodes
    dup_barcodes = barcodes[barcodes.duplicated(subset=["barcode"], keep=False)]
    if not dup_barcodes.empty:
        barcodes = barcodes.drop_duplicates(subset=["barcode"], keep="first")

    # Keep all barcodes (including unused) for later counting
    # Identify used barcodes
    used = barcodes.dropna(subset=["order_id"])

    # Orders without barcodes
    orders_with_barcodes = used["order_id"].unique()
    invalid_orders = orders[~orders["order_id"].isin(orders_with_barcodes)]

    valid_orders = orders[orders["order_id"].isin(orders_with_barcodes)]

    return valid_orders, barcodes, invalid_orders, dup_barcodes, 


def get_top_five_customers(df: pd.DataFrame) -> list[tuple[str, int]]:

    """
    Compute the top 5 customers by number of purchased tickets (barcodes).

    This function:
    - Returns the top 5 customers sorted by ticket count (descending)

    Args:
        df (pd.DataFrame):
            DataFrame with columns:
            - customer_id (str)
            - order_id (str)
            - barcodes (List[str])

    Returns:
        list[tuple[str, int]]:
            List of tuples in the format:
            [(customer_id, ticket_count), ...]
            Sorted in descending order by ticket_count
    """
    exploded = df.explode("barcodes")
    counts = exploded.groupby("customer_id")["barcodes"].count()
    top5 = counts.sort_values(ascending=False).head(5)

    return list(top5.items())



def count_unused(barcodes: pd.DataFrame) -> int:
    """
    Count the number of unused barcodes.

    Unused barcodes are defined as those without an associated order_id.

    Args:
        barcodes (pd.DataFrame)

    Returns:
        int:
            Number of barcodes where order_id is missing
    """
    return barcodes[barcodes["order_id"].isna()].shape[0]

def _assert_required_columns(df: pd.DataFrame, required: set[str], name: str):
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {sorted(missing)}. Found: {list(df.columns)}")


def validate_input_columns(orders: pd.DataFrame, barcodes: pd.DataFrame) -> None:
    """Validate that input DataFrames contain the expected columns.

    Raises:
        ValueError: if required columns are missing.
    """
    _assert_required_columns(orders, {"order_id", "customer_id"}, "orders.csv")
    _assert_required_columns(barcodes, {"barcode", "order_id"}, "barcodes.csv")

def main():
    parser = argparse.ArgumentParser(description="Process orders and barcodes")
    parser.add_argument("orders")
    parser.add_argument("barcodes")
    parser.add_argument("-o", "--output", default="output.csv")
    args = parser.parse_args()


    try:
        orders, barcodes = load_data(args.orders, args.barcodes)
        # Validate required columns early
        validate_input_columns(orders, barcodes)
    except Exception as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)

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
    for cid, count in top_five:
        print(f"{cid}, {count}")
    print ("****************************")

    print(f"Unused barcodes: {count_unused(valid_barcodes)}")


if __name__ == "__main__":
    main()