#in this version firstly i will be categorizing the tags so its easy to read on csv 
# adjusted income_data to be nested dictionary
#To build data frame using category 
import requests
import pandas as pd

CIK = "0001045810"  #  Nvidia, Inc.
BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "Use your email address"}  # Use your email address 

def get_xbrl_data():
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{CIK}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["facts"]["us-gaap"] if "facts" in data and "us-gaap" in data["facts"] else {}
    else:
        print(f"Error: {response.status_code}")
        return {}

def extract_income_data(xbrl_data):
    income_tags = {
        # Revenue Section
   "Revenues": ("Total Net Revenues", "USD", "Revenues"),
    "RevenueFromContractWithCustomerExcludingAssessedTax": ("Total Revenues", "USD", "Revenues"),

    # Cost of Revenue Section
    "FloorBrokerageExchangeAndClearanceFees": ("Brokerage and Transaction", "USD", "COR"),
    "CostOfGoodsAndServicesSold": ("CostOfGoodsAndServicesSold","USD", "COR"),
    "CostOfRevenue":("CostOfRevenue", "USD","COR"),

    # Operating Expense Section
    "AdvertisingExpense": ("Advertising Expense", "USD", "Operating Expenses"),
    "AllocatedShareBasedCompensationExpense": ("Employee Stock Pay Cost", "USD", "Operating Expenses"),
    "ResearchAndDevelopmentExpense": ("Research and Development", "USD", "Operating Expenses"),
    "CapitalizedComputerSoftwareAmortization1": ("Software Amortization", "USD", "Operating Expenses"),
    "MarketingExpense": ("Marketing", "USD", "Operating Expenses"),
   "SellingGeneralAndAdministrativeExpense": ("SG&A", "USD", "Operating Expenses"),
    "GeneralAndAdministrativeExpense": ("General and Administrative", "USD", "Operating Expenses"),
    "Depreciation": ("Depreciation", "USD", "Operating Expenses"),
    "OtherCostAndExpenseOperating": ("Other Operating Expenses", "USD", "Operating Expenses"),
    "ShareBasedCompensation": ("Share-Based Compensation", "USD", "Operating Expenses"),
    "ShortTermLeaseCost": ("Short-Term Lease Cost", "USD", "Operating Expenses"),
    "OperatingExpenses": ("Total Operating Expenses", "USD", "Operating Expenses"),

    # Non-Operating Expenses Section
    "InterestExpenseBorrowings": ("Interest Expense", "USD", "NonOperatingExpense"),
    "InterestExpense": ("Total Interest Expense", "USD", "NonOperatingExpense"),
    "InterestExpenseDebt": ("interest paid towrds debt", "USD", "NonOperatingExpense"),
    "InterestIncomeExpenseNet": ("Net Interest Expense", "USD", "NonOperatingExpense"),
    "OtherNonoperatingIncomeExpense": ("Other Non-Operating Income (Expense)", "USD", "NonOperatingExpense"),
    "ContractWithCustomerAssetCreditLossExpense": ("Credit Loss Expense", "USD", "NonOperatingExpense"),
    "AmortizationOfIntangibleAssets": ("Amortization of Intangible Assets", "USD", "NonOperatingExpense"),
    "ProvisionForDoubtfulAccounts": ("Provision for Doubtful Accounts", "USD", "NonOperatingExpense"),
    "DepreciationDepletionAndAmortization": ("Depreciation and Amortization", "USD", "NonOperatingExpense"),

    # Income Before Tax Section
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments": ("Income Before Equity Investments, Taxes, and Noncontrolling Interest", "USD", "Income Before Tax"),
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": ("Income Before Tax", "USD", "Income Before Tax"),

    # Income Taxes Section
    "CurrentIncomeTaxExpenseBenefit": ("Current Income Tax Expense (Benefit)", "USD", "Income Taxes"),
    "CurrentFederalTaxExpenseBenefit": ("Federal Income Tax Expense (Benefit)", "USD", "Income Taxes"),
    "CurrentForeignTaxExpenseBenefit": ("Foreign Income Tax Expense (Benefit)", "USD", "Income Taxes"),
    "CurrentStateAndLocalTaxExpenseBenefit": ("State and Local Income Tax Expense (Benefit)", "USD", "Income Taxes"),
    "DeferredIncomeTaxExpenseBenefit": ("Deferred Income Tax Expense (Benefit)", "USD", "Income Taxes"),
    "IncomeTaxExpenseBenefit": ("Provision for Income Taxes", "USD", "Income Taxes"),

    # Net Income Section
    "NetIncomeLoss": ("Net Income (Loss)", "USD", "Net Income"),
    "NetIncomeLossAvailableToCommonStockholdersBasic": ("Net Income (Loss) Attributable to Common Stockholders (Basic)", "USD", "Net Income"),
    "NetIncomeLossAvailableToCommonStockholdersDiluted": ("Net Income (Loss) Attributable to Common Stockholders (Diluted)", "USD", "Net Income"),

    # Per Share Metrics Section
    "EarningsPerShareBasic": ("Earnings Per Share (Basic)", "pure", "Per Share Metrics"),
    "EarningsPerShareDiluted": ("Earnings Per Share (Diluted)", "pure", "Per Share Metrics"),
    "WeightedAverageNumberOfSharesOutstandingBasic": ("Weighted-Average Shares (Basic)", "shares", "Per Share Metrics"),
    "WeightedAverageNumberOfDilutedSharesOutstanding": ("Weighted-Average Shares (Diluted)", "shares", "Per Share Metrics")
    }
    
    # Update the dictionary to have key as category and values as tags, years and values 
    income_data = {
        "Revenues":{},
        "COR":{},
        "Operating Expenses":{},
        "NonOperatingExpense":{},
        "Income Before Tax":{},
        "Income Taxes":{},
        "Net Income":{},
        "Per Share Metrics":{}
        }
    
    # Extract data for each tag
    for tag, (label, unit, category) in income_tags.items():
        if tag in xbrl_data:
            units = xbrl_data[tag]["units"]
            print(f"Checking tag '{tag}' – Available units: {list(units.keys())}, expected: '{unit}'")
            if unit in units:
                entries = units[unit]
                print(f"Tag: {tag}, Label: {label}, , Category: {category}, Entries for {unit}:")
                if label not in income_data[category]:
                    income_data[category][label] = {}
                for entry in entries:
                    form = entry.get("form")
                    year = entry.get("fy")
                    if not year:
                        end_date = entry.get("end")
                        if end_date and len(end_date) >= 4:
                            year = int(end_date[:4])
                    if year and 2014 <= year <= 2025 and form in ["10-K", "10-K/A"]:  #Use any Date Range you want to analyze
                        value = entry["val"] / 1_000_000 if unit == "USD" else entry["val"]
                        print(f"  Year: {year}, Form: {form}, Value: {value}")
                        income_data[category][label][year] = value
            else:
                print(f"Tag {tag} does not have expected unit '{unit}'. Available units: {list(units.keys())}")
        else:
            print(f"Tag {tag} not found in XBRL data.")
    
    return income_data

def create_dataframe(income_data):
    # Collect all unique years across all categories and items
    years = set()
    for category, items in income_data.items():
        for label, year_data in items.items():
            years.update(year_data.keys())
    years = sorted(years)  # Sort years in ascending order

    # Define the order of categories
    category_order = [
        "Revenues",
        "COR",
        "Operating Expenses",
        "NonOperatingExpense",
        "Income Before Tax",
        "Income Taxes",
        "Net Income",
        "Per Share Metrics"
    ]
    

    # List to hold sub-DataFrames for each category
    dfs = []

    # Build a sub-DataFrame for each category
    for category in category_order:
        if category in income_data and income_data[category]:  # Check if category has data
            # Create a section header row
            header_row = pd.DataFrame([[f"**{category}**", ""] + [None] * len(years)], columns=["Category", "Item"] + years)

            # Build data for items in this category
            category_data = []
            for label in sorted(income_data[category].keys()):  # Sort labels alphabetically for consistency
                row = [label] + [income_data[category][label].get(year, None) for year in years]
                category_data.append(row)

            # Create a sub-DataFrame for the items in this category
            category_df = pd.DataFrame(category_data, columns=["Item"] + years)

            # Concatenate the header and the category items
            dfs.extend([header_row, category_df])

    # Concatenate all sub-DataFrames vertically
    final_df = pd.concat(dfs, ignore_index=True)

    return final_df

def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
if __name__ == "__main__":
    xbrl_data = get_xbrl_data()
    income_data = extract_income_data(xbrl_data)
    print("\nExtracted Income Data (2020-2024, 10-K only, in millions):")
    for category, items in income_data.items():
        print(f"\nCategory: {category}")
        for label, years in items.items():
            print(f"  {label}: {dict(sorted(years.items()))}")
    
    df = create_dataframe(income_data)
    print("\nDataFrame:")
    print(df)

    
      # DYNAMIC FILENAME LOGIC
    # We create the filename using the CIK variable from the top of the script
    dynamic_filename = f"{CIK}_Income_Statement.csv" #Search for the file name in download folder 
    save_to_csv(df, dynamic_filename)