import requests
import pandas as pd

CIK = "0001045810"  # NVIDIA Corporation, you can use any CIK Number (Nvidia is just an example) 
BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "Use your email address"} # Use your email address 

def get_xbrl_data():
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{CIK}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["facts"]["us-gaap"] if "facts" in data and "us-gaap" in data["facts"] else {}
    else:
        print(f"Error: {response.status_code}")
        return {}

def extract_cash_flow_data(xbrl_data):
    cash_flow_tags = {
        # Operating Cash Flow
        "DepreciationDepletionAndAmortization": ("Depreciation and amortization", "USD", "Operating Cash Flow"),
        "ImpairmentOfLongLivedAssetsHeldForUse": ("Impairment of long-lived assets", "USD", "Operating Cash Flow"),
        "ProvisionForDoubtfulAccounts": ("Provision for credit losses", "USD", "Operating Cash Flow"),
        "ShareBasedCompensation": ("Share-based compensation", "USD", "Operating Cash Flow"),
        "OtherOperatingActivitiesCashFlowStatement": ("Other", "USD", "Operating Cash Flow"),
        "CashAndSecuritiesSegregatedUnderFederalAndOtherRegulations": ("Segregated securities under federal and other regulations", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInBrokerageReceivables": ("Receivables from brokers, dealers, and clearing organizations", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInAccountsReceivable": ("Receivables from users, net", "USD", "Operating Cash Flow"),
        "SecuritiesBorrowed": ("Securities borrowed", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInBrokerageReceivables": ("Deposits with clearing organizations", "USD", "Operating Cash Flow"),  # Note: Repeated tag, assuming separate use
        "IncreaseDecreaseInPrepaidExpense": ("Current and non-current prepaid expenses", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInOtherOperatingAssets": ("Other current and non-current assets", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities": ("Accounts payable and accrued expenses", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInPayablesToCustomers": ("Payables to users", "USD", "Operating Cash Flow"),
        "SecuritiesLoaned": ("Securities loaned", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInOtherOperatingLiabilities": ("Other current and non-current liabilities", "USD", "Operating Cash Flow"),
        "CashAndSecuritiesSegregatedUnderSecuritiesExchangeCommissionRegulation": ("Net cash provided by (used in) operating activities", "USD", "Operating Cash Flow"),
        "IncomeTaxExpenseBenefit": ("Income Tax expense", "USD", "Operating Cash Flow"),  # Added as per Operating Activity

        # Investing Cash Flow
        "PaymentsForProceedsFromOtherInvestingActivities": ("Other", "USD", "Investing Cash Flow"),
        "PaymentsToDevelopSoftware": ("Capitalization of internally developed software", "USD", "Investing Cash Flow"),
        "PaymentsToAcquireBusinessesNetOfCashAcquired": ("Acquisitions of a business, net of cash acquired", "USD", "Investing Cash Flow"),
        "PaymentsToAcquirePropertyPlantAndEquipment": ("Purchase of property, plant, and equipment", "USD", "Investing Cash Flow"),
        "PaymentsToAcquireProductiveAssets": ("Payments To Acquire Productive Assets", "USD", "Investing Cash Flow"),
        "PaymentsToAcquireOtherInvestments": ("PaymentsToAcquireOtherInvestments", "USD", "Investing Cash Flow"),
        "PaymentsToAcquireAvailableForSaleSecurities": ("PaymentsToAcquireAvailableForSaleSecurities", "USD", "Investing Cash Flow"),

        "CapitalExpenditures" : ("Cash spent on assets more than 1 year", "USD", "Investing Cash Flow"),
        "CapitalExpendituresIncurredButNotYetPaid": ("Capital Expenditures Incurred but Not yet Paid", "USD", "Investing Cash Flow"),
        "NetCashProvidedByUsedInInvestingActivities": ("Net cash used in investing activities", "USD", "Investing Cash Flow"),

        # Financing Cash Flow
        "ProceedsFromIssuanceInitialPublicOffering": ("Proceeds from issuance of common stock in connection with initial public offering, net of offering costs", "USD", "Financing Cash Flow"),
        "PaymentsForRepurchaseOfCommonStock": ("Common Stock Payments", "USD", "Financing Cash Flow"),
        "NetCashProvidedByUsedInFinancingActivities": ("Net cash provided by financing activities", "USD", "Financing Cash Flow"),
        "PaymentsOfDebtIssuanceCosts": ("Payments of debt issuance costs", "USD", "Financing Cash Flow"),  # Naming convention inferred
        "PaymentsToAcquireHeldToMaturitySecurities": ("Payments to acquire held-to-maturity securities", "USD", "Financing Cash Flow"),  # Naming convention inferred
        "ProceedsFromIssuanceOfSecuredDebt": ("Proceeds from issuance of secured debt", "USD", "Financing Cash Flow"),  # Naming convention inferred
        "RepaymentsOfSecuredDebt": ("Repayments of secured debt", "USD", "Financing Cash Flow"),  # Naming convention inferred
        "NetCashProvidedByUsedInFinancingActivities": ("NetCashProvidedByUsedInFinancingActivities", "USD", "Financing Cash Flow"),  # Naming convention inferred
        "ProceedsFromIssuanceOfCommonStock": ("Amount received from Issuance of Common Stock ", "USD", "Financing Cash Flow"),  # Naming convention inferred


        # Effect of Exchange Rates
        "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": ("Effect of foreign exchange rate on cash", "USD", "Effect of Exchange Rates"),

        # Net Change in Cash
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect": ("Changes in Cash", "USD", "Net Change in Cash"),

        # Ending Cash Balance
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": ("Cash, cash equivalents, segregated cash and restricted cash, end of the period", "USD", "Ending Cash Balance"),
        "CashSegregatedUnderOtherRegulations": ("Segregated cash, end of the period", "USD", "Ending Cash Balance"),
        "CashAndCashEquivalentsAtCarryingValue": ("Cash and cash equivalents, end of the period", "USD", "Ending Cash Balance"),
        "RestrictedCash": ("Restricted cash (current and non-current), end of the period", "USD", "Ending Cash Balance"),
    }

    # Missing tags with naming conventions provided but no XBRL tag (not included unless tags are found)
    # - "Net income (loss)"
    # - "Change in fair value of convertible notes and warrant liability"
    # - "Purchase of property, plants, and other productive assets"
    # - "Purchase of investments"
    # - "Sales of investments"

    cash_flow_data = {
        "Operating Cash Flow": {},
        "Investing Cash Flow": {},
        "Financing Cash Flow": {},
        "Effect of Exchange Rates": {},
        "Net Change in Cash": {},
        "Ending Cash Balance": {},
    }

    # Extract data for each tag
    for tag, (label, unit, category) in cash_flow_tags.items():
        if tag in xbrl_data:
            units = xbrl_data[tag]["units"]
            if unit in units:
                entries = units[unit]
                print(f"Tag: {tag}, Label: {label}, Category: {category}, Entries for {unit}:")
                if label not in cash_flow_data[category]:
                    cash_flow_data[category][label] = {}
                for entry in entries:
                    year = entry.get("fy")
                    form = entry.get("form")
                    if year and 2014 <= year <= 2025 and form == "10-K": #Use any Date Range you want to analyze
                        value = entry["val"] / 1_000_000 if unit == "USD" else entry["val"]
                        print(f"  Year: {year}, Form: {form}, Value: {value}")
                        cash_flow_data[category][label][year] = value
            else:
                print(f"Tag {tag} does not have expected unit '{unit}'. Available units: {list(units.keys())}")
        else:
            print(f"Tag {tag} not found in XBRL data.")

    return cash_flow_data

def create_dataframe(cash_flow_data):
    # Collect all unique years across all categories and items
    years = set()
    for category, items in cash_flow_data.items():
        for label, year_data in items.items():
            years.update(year_data.keys())
    years = sorted(years)  # Sort years in ascending order

    category_order = [
        "Operating Cash Flow",
        "Investing Cash Flow",
        "Financing Cash Flow",
        "Effect of Exchange Rates",
        "Net Change in Cash",
        "Ending Cash Balance",
    ]
    dfs = []

    # Build a sub-DataFrame for each category
    for category in category_order:
        if category in cash_flow_data and cash_flow_data[category]:  # Check if category has data
            # Create a section header row
            header_row = pd.DataFrame([[f"**{category}**", ""] + [None] * len(years)], columns=["Category", "Item"] + years)

            # Build data for items in this category
            category_data = []
            for label in sorted(cash_flow_data[category].keys()):  # Sort labels alphabetically for consistency
                row = [label] + [cash_flow_data[category][label].get(year, None) for year in years]
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
    cash_flow_data = extract_cash_flow_data(xbrl_data)
    print("\nExtracted Cash Flow Data (2020-2024, 10-K only, in millions):")
    for category, items in cash_flow_data.items():
        print(f"\nCategory: {category}")
        for label, years in items.items():
            print(f"  {label}: {dict(sorted(years.items()))}")

    df = create_dataframe(cash_flow_data)
    print("\nDataFrame:")
    print(df)
    
      # DYNAMIC FILENAME LOGIC
    # We create the filename using the CIK variable from the top of the script
    dynamic_filename = f"{CIK}_Cashflow_statement.csv" #Search for the file name in download folder 
    save_to_csv(df, dynamic_filename)