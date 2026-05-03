# Tiqets 
## Solution outline
The project delivers the requirements provided in 'Tiqets Programming Assignment - CSV files.pdf '. 

- main.py: is the entry point to the application
    - Arguments:
        - Two CSVs (orders, barcodes) with the following columns:
        - order_id,customer_id
        - barcode,order_id
        -Output path for the exported output
    - Expected Output:
        - Exported CSV with all the barcodes and orders_ids per
customer
        - Prints out the Top five customers with the most tickets
        - Prints out the amount of unusued barcodes
        - Logs any duplicate barcodes or invalid orders
    - Performs processing of the files, validation, analysis and outputs the results in a CSV
- data directory
    - Contains our dataset for barcodes, orders (including invalid ones for testing)
- tests directory
    - Includes unit tests for various use cases including:
        - Validation on CSV columns
        - Basic output creation
        - Duplicate barcodes
        - Invalid Orders (orders without barcode)
        - Top five customers
        - Count of unused barcodes


## Prerequisites
- Python 3.14

## Dependencies

### Create virtual environment 
```python -m venv .new_venv```

### Activate virtual environment 

Windows:
```.new_venv/Scripts/activate```

Mac: 
```.new_venv/bin/activate```

### Install dependencies
```pip install -r requirements.txt```

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