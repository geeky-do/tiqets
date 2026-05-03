run-tests:
	pytest tests/test_main.py	

run-with-data:
	python main.py data/orders.csv data/barcodes.csv -o export/export.csv

run-with-args:
	python main.py $(orders) $(barcodes) -o $(export)	