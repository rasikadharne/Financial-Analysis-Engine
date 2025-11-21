# Financial-Analysis-Engine & SEC EDGAR Pipeline
A Python-based tool to extract SEC EDGAR data, consolidate financial statements, and perform automated ratio analysis.



## Overview
This project is a Python-based financial modeling tool that automates the extraction of fundamental data from the SEC EDGAR database. It parses XBRL data to generate formatted Income Statements, Balance Sheets, and Cash Flows, and consolidates them into a Master Analysis file for ratio calculation and visualization.

## Features

Current Features (Completed Features) 

* **Automated Extraction:** Pulls 10-K data directly from the SEC API. 
* **Data Transformation:** Cleans and standardizes raw XBRL tags.
* **Retrive financial data for any company publicly traded having a CIK number:** insert CIK number of the company you want to analyze.
* **Flexible date range to retrive data :** Data from any time period can be retrived by providing date range, provided the data is avaiable within EDGAR.
* * **Formatted Income Statement CSV available for download:** XBRL Tags supporting income statement formatted to analyze.
* **Formatted Balance Sheet  CSV available for download:** XBRL Tags supporting balance sheet formatted to analyze.
* **Formatted Cashflow CSV available for download:** XBRL Tags supporting cashflow formatted to analyze.
* **CaseStudies:** Finanical analysis of different companies that interests me.

Future Features (WIP)
  
* **Consolidation:** Merges three separate financial statements into a single time-series dataset.  --> WIP for this step  to automate 
* **Ratio Analysis:** Calculates ROE, ROA, Net Margin, and Free Cash Flow.--> WIP for this step to automate ratio generation 
* **Visualization:** Generates dual-axis charts (Revenue vs. Margins).--> WIP for this step to automate ratio generation 

## Project Organization
* `src/`: Contains the Python source code (extractors and analysis engine).
* `case_studies/`: Stores the output data and graphs for analyzed companies.
* `requirements.txt`: Lists all Python dependencies.


## Prerequisites
* Python 3.8+
* A valid email address (required for SEC API identification)
* CIK Number
* Provide Date Range 

## Installation
1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Financial-Analysis-Engine.git](https://github.com/YOUR_USERNAME/Financial-Analysis-Engine.git)
    ```
2.  Navigate to the directory:
    ```bash
    cd Financial-Analysis-Engine
    ```
3.  Install required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (Crucial Step)
**You must configure your User-Agent before running.**

1.  Open `src/income_statement.py` (and the other scripts in `src/`).
2.  Update the `HEADERS` dictionary with your email address:
    ```python
    HEADERS = {"User-Agent": "your-email@example.com"}
    ```
3.  Update the `CIK` variable to the company you wish to analyze:
    ```python
    CIK = "0001045810"  # Example: NVIDIA
    ```
4. Provide range for years  you wish to analyze:
    ```if year and 2014 <= year <= 2025 # for analzing from 2014 to 2025, this part can be found within FOR Loop of the code for each statement 
    ```

## Usage
Run the scripts in this order:

1.  **Extract Data:**
    ```bash
    python src/income_statement.py
    python src/balance_sheet.py
    python src/cashflow.py    # you can run in any order like balance sheet, income statement and cash flow. Providing this order for a good practice. 
    ```


## Outputs
* **`{CIK}_Income_Statement.csv`**: Find this file within downloads folder
* **`{CIK}_balance_sheet.csv`**: Find this file within downloads folder
* **`{CIK}_Cashflow_statement.csv`**: Find this file within downloads folder
* **Feel free to start your analysis 

---

