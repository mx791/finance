# Data driven investment

Before touching anything, make sure to have the required dependencies installed locally :
```
pip install -r requirements.txt
```

## Fetching data
To create & enrich the dataset, two stepps :
- `python data-aquire/list_symbols.py` : create etl_list.csv and funds.csv, which is the list of all availables symbols
- `python data-aquire/fetch_stocks.py` : download dayly quotations for all availables financial products


## Analysis
First run the return anaylis script, which computes a few metrics for each financial products. Theses metrics are used later. To do so, run: 

```
python analysis/returns_analysis.py
```

The dashboard can now be launched, using :

```
python analysis/web_comparator.py
```

The dashboard can now be accessed though your browser, at the adress : `http://localhost:8050/`
