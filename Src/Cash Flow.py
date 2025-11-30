import requests
import pandas as pd
from datetime import datetime  # NEW: for period-length logic

CIK = "0001045810"  # NVIDIA Corporation, you can use any CIK Number
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
        # NOTE: tag repeated; this second one will overwrite the first in Python
        "IncreaseDecreaseInBrokerageReceivables": ("Deposits with clearing organizations", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInPrepaidExpense": ("Current and non-current prepaid expenses", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInOtherOperatingAssets": ("Other current and non-current assets", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities": ("Accounts payable and accrued expenses", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInPayablesToCustomers": ("Payables to users", "USD", "Operating Cash Flow"),
        "SecuritiesLoaned": ("Securities loaned", "USD", "Operating Cash Flow"),
        "IncreaseDecreaseInOtherOperatingLiabilities": ("Other current and non-current liabilities", "USD", "Operating Cash Flow"),
        "CashAndSecuritiesSegregatedUnderSecuritiesExchangeCommissionRegulation": ("Net cash provided by (used in) operating activities", "USD", "Operating Cash Flow"),
        "IncomeTaxExpenseBenefit": ("Income Tax expense", "USD", "Operating Cash Flow"),

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
        "PaymentsOfDebtIssuanceCosts": ("Payments of debt issuance costs", "USD", "Financing Cash Flow"),
        "PaymentsToAcquireHeldToMaturitySecurities": ("Payments to acquire held-to-maturity securities", "USD", "Financing Cash Flow"),
        "ProceedsFromIssuanceOfSecuredDebt": ("Proceeds from issuance of secured debt", "USD", "Financing Cash Flow"),
        "RepaymentsOfSecuredDebt": ("Repayments of secured debt", "USD", "Financing Cash Flow"),
        # NOTE: this overwrites the previous NetCashProvidedByUsedInFinancingActivities label
        "NetCashProvidedByUsedInFinancingActivities": ("NetCashProvidedByUsedInFinancingActivities", "USD", "Financing Cash Flow"),
        "ProceedsFromIssuanceOfCommonStock": ("Amount received from Issuance of Common Stock ", "USD", "Financing Cash Flow"),

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

    cash_flow_data = {
        "Operating Cash Flow": {},
        "Investing Cash Flow": {},
        "Financing Cash Flow": {},
        "Effect of Exchange Rates": {},
        "Net Change in Cash": {},
        "Ending Cash Balance": {},
    }

    # Annual-type forms (same logic as income statement)
    annual_forms = {"10-K", "10-K/A", "20-F", "20-F/A", "40-F", "40-F/A"}

    def get_entry_year(entry):
        """Use fy as fiscal year; fallback to end-date year if fy missing."""
        fy = entry.get("fy")
        if fy is not None:
            try:
                return int(fy)
            except ValueError:
                pass
        end = entry.get("end")
        if end and len(end) >= 4:
            try:
                return int(end[:4])
            except ValueError:
                pass
        return None

    def get_duration_days(entry):
        start = entry.get("start")
        end = entry.get("end")
        if not (start and end):
            return 0
        try:
            return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).days
        except Exception:
            return 0

    # Extract data for each tag
    for tag, (label, unit, category) in cash_flow_tags.items():
        if tag not in xbrl_data:
            print(f"Tag {tag} not found in XBRL data.")
            continue

        units = xbrl_data[tag]["units"]
        print(f"\nChecking tag '{tag}' – Available units: {list(units.keys())}, expected: '{unit}'")
        if unit not in units:
            print(f"Tag {tag} does not have expected unit '{unit}'. Available units: {list(units.keys())}")
            continue

        entries = units[unit]
        print(f"Tag: {tag}, Label: {label}, Category: {category}, Entries for {unit}:")

        # year -> best (longest-duration) annual entry
        annual_by_year = {}

        for entry in entries:
            form = entry.get("form")
            if form not in annual_forms:
                continue

            year = get_entry_year(entry)
            if year is None:
                continue

            # Restrict to your analysis window
            if not (2014 <= year <= 2025):
                continue

            duration_days = get_duration_days(entry)

            # Ensure we only keep annual-type periods:
            qtrs = entry.get("qtrs")
            if qtrs is not None:
                try:
                    if int(qtrs) != 4:
                        continue  # skip non-annual periods
                except ValueError:
                    if duration_days < 300:
                        continue
            else:
                # No qtrs field -> require roughly a full year
                if duration_days < 300:
                    continue

            # Make sure the end-date year matches the fiscal year
            end = entry.get("end")
            end_year = None
            if end and len(end) >= 4:
                try:
                    end_year = int(end[:4])
                except ValueError:
                    pass

            if end_year is not None and end_year != year:
                # Filters out re-reported calendar-year frames under later fy
                continue

            value = entry["val"] / 1_000_000 if unit == "USD" else entry["val"]

            prev = annual_by_year.get(year)
            # Keep the longest-duration annual entry for that year
            if (prev is None) or (duration_days > prev["duration_days"]):
                annual_by_year[year] = {
                    "duration_days": duration_days,
                    "value": value,
                    "form": form,
                    "start": entry.get("start"),
                    "end": entry.get("end"),
                    "frame": entry.get("frame"),
                    "qtrs": entry.get("qtrs"),
                }

        if annual_by_year:
            if label not in cash_flow_data[category]:
                cash_flow_data[category][label] = {}
            for year, info in sorted(annual_by_year.items()):
                cash_flow_data[category][label][year] = info["value"]
                print(
                    f"  Year: {year}, Form: {info['form']}, "
                    f"Frame: {info['frame']}, qtrs: {info['qtrs']}, "
                    f"Start: {info['start']}, End: {info['end']}, "
                    f"Duration: {info['duration_days']} days, "
                    f"Value (millions if USD): {info['value']}"
                )
        else:
            print("  No annual-worthy entries found for this tag/unit in the chosen year range.")

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
            header_row = pd.DataFrame([[f"**{category}**", ""] + [None] * len(years)],
                                      columns=["Category", "Item"] + years)

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
    print("\nExtracted Cash Flow Data (2014–2025, annual forms only, in millions where USD):")
    for category, items in cash_flow_data.items():
        print(f"\nCategory: {category}")
        for label, years in items.items():
            print(f"  {label}: {dict(sorted(years.items()))}")

    df = create_dataframe(cash_flow_data)
    print("\nDataFrame:")
    print(df)
    
    # DYNAMIC FILENAME LOGIC
    dynamic_filename = f"{CIK}_Cashflow_statement.csv"
    save_to_csv(df, dynamic_filename)
