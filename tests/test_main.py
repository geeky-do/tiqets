from main import load_data, build_output, validate

def test_build_output_basic(tmp_path):
    orders_csv = tmp_path / "orders.csv"
    barcodes_csv = tmp_path / "barcodes.csv"

    orders_csv.write_text("order_id,customer_id\n1,A\n2,B\n")
    barcodes_csv.write_text("barcode,order_id\nb1,1\nb2,1\nb3,2\n")

    orders, barcodes = load_data(str(orders_csv), str(barcodes_csv))
    valid_orders, valid_barcodes = validate(orders, barcodes)
    output = build_output(valid_orders, valid_barcodes)

    assert len(output) == 2
    assert output.loc[output.order_id == '1', 'barcodes'].iloc[0] == ['b1', 'b2']