from main import load_data, build_output, validate, count_unused, get_top_five_customers
import pandas as pd


def test_build_output_basic(tmp_path):
    orders_csv = tmp_path / "orders.csv"
    barcodes_csv = tmp_path / "barcodes.csv"

    orders_csv.write_text("order_id,customer_id\n1,A\n2,B\n")
    barcodes_csv.write_text("barcode,order_id\nb1,1\nb2,1\nb3,2\n")

    orders, barcodes = load_data(str(orders_csv), str(barcodes_csv))
    valid_orders, valid_barcodes, _, _ = validate(orders, barcodes)
    output = build_output(valid_orders, valid_barcodes)

    assert len(output) == 2
    assert output.loc[output.order_id == '1', 'barcodes'].iloc[0] == ['b1', 'b2']

def test_duplicate_barcodes_removed(tmp_path):
    orders_csv = tmp_path / "orders.csv"
    barcodes_csv = tmp_path / "barcodes.csv"

    orders_csv.write_text("order_id,customer_id\n1,A\n")
    barcodes_csv.write_text("barcode,order_id\nb1,1\nb1,1\n")

    orders, barcodes = load_data(str(orders_csv), str(barcodes_csv))
    _, valid_barcodes, _, _ = validate(orders, barcodes)

    assert valid_barcodes['barcode'].nunique() == 1


def test_orders_without_barcodes_removed(tmp_path):
    orders_csv = tmp_path / "orders.csv"
    barcodes_csv = tmp_path / "barcodes.csv"

    orders_csv.write_text("order_id,customer_id\n1,A\n2,B\n")
    barcodes_csv.write_text("barcode,order_id\nb1,1\n")

    orders, barcodes = load_data(str(orders_csv), str(barcodes_csv))
    valid_orders, _, _, _ = validate(orders, barcodes)

    assert len(valid_orders) == 1
    assert valid_orders.iloc[0].order_id == '1'


def test_unused_barcodes_count(tmp_path):
    barcodes_csv = tmp_path / "barcodes.csv"
    orders_csv = tmp_path / "orders.csv"

    orders_csv.write_text("order_id,customer_id\n1,A\n")
    barcodes_csv.write_text("barcode,order_id\nb1,1\nb2,\n")

    orders, barcodes = load_data(str(orders_csv), str(barcodes_csv))
    _, valid_barcodes, _, _ = validate(orders, barcodes)

    assert count_unused(valid_barcodes) == 1

def test_top_five_customers(capsys):
    df = pd.DataFrame({
        "customer_id": ["A", "A", "B", "B", "B", "C", "C", "D", "E", "F"],
        "order_id":    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        "barcodes": [
            ["b1", "b2"],      # A -> 2
            ["b3"],            # A -> 1 (total 3)
            ["b4"],            # B -> 1
            ["b5", "b6"],    # B -> 2
            ["b7"],            # B -> 1 (total 4)
            ["b8"],            # C -> 1
            ["b9"],            # C -> 1 (total 2)
            ["b10"],           # D -> 1
            ["b11"],           # E -> 1
            ["b12"]            # F -> 1
        ]
    })
    result = get_top_five_customers(df)
    expected = [
        ("B", 4),
        ("A", 3),
        ("C", 2),
        ("D", 1),
        ("E", 1),
    ]

    assert result == expected
