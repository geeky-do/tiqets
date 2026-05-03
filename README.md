# Tiqets 
## Solution outline

Based on the requirements outlined in 'Tiqets Programming Assignment - CSV files.pdf ' the following solution was created:

- main.py --> is the entry point to the application
    - TBA
- data directory
    - Contains our dataset for barcodes, orders

## Prerequisites
- Python 3.14
## Dependencies
Install dependencies via the command

``` ```

## Unit testing
Run the tests via the command

```pytest tests/test_main.py```

## Run the Code
Run the application via the command
```python main.py data/orders.csv data/barcodes.csv -o export/export.csv ``` 

## UML 

![alt text][logo]

[logo]: diagram.png "UML"

## SQL Schema
```
SQL_SCHEMA = """
CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY
);

CREATE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR REFERENCES customers(customer_id)
);

CREATE TABLE barcodes (
    barcode VARCHAR PRIMARY KEY,
    order_id VARCHAR NULL REFERENCES orders(order_id)
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_barcodes_order_id ON barcodes(order_id);
"""
```