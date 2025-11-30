import requests
import pandas as pd
from datetime import datetime  # NEW: for duration computation if needed

CIK = "0001045810"  # NVIDIA Corporation, you can use any CIK Number (Nvidia is just an example) 
BASE_URL = "https://data.sec.gov"
HEADERS = {"User-Agent": "your-email@example.com"}   # Use your email address 

def get_xbrl_data():
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{CIK}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["facts"]["us-gaap"] if "facts" in data and "us-gaap" in data["facts"] else {}
    else:
        print(f"Error: {response.status_code}")
        return {}

def extract_balance_sheet_data(xbrl_data):
    balance_sheet_tags = {
        # Total Assets
        "Assets": ("Total assets", "USD", "Total Assets"),

        # Current Assets
        "AssetsCurrent": ("Total current assets", "USD", "Current Assets"),
        "CashAndCashEquivalentsAtCarryingValue": ("Cash and cash equivalents", "USD", "Current Assets"),
        "AccountsReceivableNetCurrent": ("Accounts receivable, net", "USD", "Current Assets"),
        "InventoryNet": ("Inventory, net", "USD", "Current Assets"),
        "PrepaidExpenseCurrent": ("Prepaid expenses", "USD", "Current Assets"),
        "MarketableSecuritiesCurrent": ("Marketable securities, current", "USD", "Current Assets"),
        "DeferredTaxAssetsLiabilitiesNetCurrent": ("Deferred tax assets, current", "USD", "Current Assets"),
        "OtherAssetsCurrent": ("Other current assets", "USD", "Current Assets"),
        "AvailableForSaleSecuritiesDebtMaturitiesWithinOneYearFairValue":(
            "AvailableForSaleSecuritiesDebtMaturitiesWithinOneYearFairValue", "USD", "Current Assets"
        ),
        "InventoryWorkInProcess":("InventoryWorkInProcess","USD","Current Assets"),
        "InventoryFinishedGoods":("InventoryFinishedGoods","USD","Current Assets"),
        
        # Non-Current Assets
        "AssetsNoncurrent": ("Total non-current assets", "USD", "Non-Current Assets"),
        "PropertyPlantAndEquipmentNet": ("Property, plant, and equipment, net", "USD", "Non-Current Assets"),
        "OperatingLeaseRightOfUseAsset": ("Operating lease right-of-use assets", "USD", "Non-Current Assets"),
        "FinanceLeaseRightOfUseAsset": ("Finance lease right-of-use assets", "USD", "Non-Current Assets"),
        "Goodwill": ("Goodwill", "USD", "Non-Current Assets"),
        "IntangibleAssetsNetExcludingGoodwill": ("Intangible assets, net", "USD", "Non-Current Assets"),
        "LongTermInvestments": ("Long-term investments", "USD", "Non-Current Assets"),
        "DeferredTaxAssetsLiabilitiesNetNoncurrent": ("Deferred tax assets, non-current", "USD", "Non-Current Assets"),
        "PrepaidExpenseNoncurrent": ("Prepaid expenses, non-current", "USD", "Non-Current Assets"),
        "OtherAssetsNoncurrent": ("Other non-current assets", "USD", "Non-Current Assets"),
        "EquitySecuritiesWithoutReadilyDeterminableFairValueAmount":(
            "EquitySecuritiesWithoutReadilyDeterminableFairValueAmount", "USD", "Non-Current Assets"
        ),
        "DeferredTaxAssetsGross": ("DeferredTaxAssetsGross","USD", "Non-Current Assets"),
        "DeferredIncomeTaxLiabilities":("DeferredIncomeTaxLiabilities","USD", "Non-Current Assets"),
        
        # Total Liabilities
        "Liabilities": ("Total liabilities", "USD", "Total Liabilities"),
        "OperatingLeasesFutureMinimumPaymentsDueCurrent" :(
            "OperatingLeasesFutureMinimumPaymentsDueCurrent", "USD", "Total Liabilities"
        ),
        
        # Current Liabilities
        "LiabilitiesCurrent": ("Total current liabilities", "USD", "Current Liabilities"),
        "AccountsPayableCurrent": ("Accounts payable", "USD", "Current Liabilities"),
        "AccruedLiabilitiesCurrent": ("Accrued liabilities", "USD", "Current Liabilities"),
        "DeferredRevenueCurrent": ("Deferred revenue, current", "USD", "Current Liabilities"),
        "ShortTermBorrowings": ("Short-term debt", "USD", "Current Liabilities"),
        "OperatingLeaseLiabilityCurrent": ("Operating lease liabilities, current", "USD", "Current Liabilities"),
        "FinanceLeaseLiabilityCurrent": ("Finance lease liabilities, current", "USD", "Current Liabilities"),
        "TaxesPayableCurrent": ("Income taxes payable", "USD", "Current Liabilities"),
        "OtherCurrentLiabilities": ("Other current liabilities", "USD", "Current Liabilities"),
        
        # Non-Current Liabilities
        "AccruedRentNoncurrent" : ("AccruedRentNoncurrent", "USD", "Current Liabilities"),  # as in your original
        "LiabilitiesNoncurrent": ("Total non-current liabilities", "USD", "Non-Current Liabilities"),
        "LongTermDebtNoncurrent": ("Long-term debt", "USD", "Non-Current Liabilities"),
        "DeferredRevenueNoncurrent": ("Deferred revenue, non-current", "USD", "Non-Current Liabilities"),
        "OperatingLeaseLiabilityNoncurrent": ("Operating lease liabilities, non-current", "USD", "Non-Current Liabilities"),
        "FinanceLeaseLiabilityNoncurrent": ("Finance lease liabilities, non-current", "USD", "Non-Current Liabilities"),
        "DeferredTaxLiabilitiesNoncurrent": ("Deferred tax liabilities, non-current", "USD", "Non-Current Liabilities"),
        "OtherNoncurrentLiabilities": ("Other non-current liabilities", "USD", "Non-Current Liabilities"),
        
        # Equity
        "StockholdersEquity": ("Total stockholders' equity", "USD", "Equity"),
        "CommonStockValue": ("Common stock", "USD", "Equity"),
        "PreferredStockValue": ("Preferred stock", "USD", "Equity"),
        "AdditionalPaidInCapital": ("Additional paid-in capital", "USD", "Equity"),
        "RetainedEarningsAccumulatedDeficit": ("Retained earnings (accumulated deficit)", "USD", "Equity"),
        "TreasuryStockValue": ("Treasury stock", "USD", "Equity"),
        "AccumulatedOtherComprehensiveIncomeLossNetOfTax": ("Accumulated other comprehensive income (loss)", "USD", "Equity"),
        "NoncontrollingInterest": ("Noncontrolling interest", "USD", "Equity"),
        "CommonStockSharesIssued": ("Common stock shares issued", "shares", "Equity"),
        "CommonStockSharesOutstanding": ("Common stock shares outstanding", "shares", "Equity"),
        
        # Total Liabilities and Equity
        "LiabilitiesAndStockholdersEquity": ("Total liabilities and stockholders' equity", "USD", "Total Liabilities and Equity")
    }

    balance_sheet_data = {
        "Total Assets": {},
        "Current Assets": {},
        "Non-Current Assets": {},
        "Total Liabilities": {},
        "Current Liabilities": {},
        "Non-Current Liabilities": {},
        "Equity": {},
        "Total Liabilities and Equity": {},
    }

    # Annual-type forms (same as income/cash flow)
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

    # Extract data for each tag using annual-selection logic
    for tag, (label, unit, category) in balance_sheet_tags.items():
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

        # year -> best (longest-duration) entry for that year
        annual_by_year = {}

        for entry in entries:
            form = entry.get("form")
            if form not in annual_forms:
                continue

            year = get_entry_year(entry)
            if year is None:
                continue

            # Analysis window
            if not (2014 <= year <= 2025):
                continue

            duration_days = get_duration_days(entry)

            # Use qtrs to ensure annual snapshot when available
            qtrs = entry.get("qtrs")
            if qtrs is not None:
                try:
                    if int(qtrs) != 4:
                        continue  # skip non-annual periods (e.g., quarterly)
                except ValueError:
                    # if qtrs is weird, we just don't filter by it
                    pass

            # Ensure end-year matches fy to avoid re-reported calendar frames
            end = entry.get("end")
            end_year = None
            if end and len(end) >= 4:
                try:
                    end_year = int(end[:4])
                except ValueError:
                    pass

            if end_year is not None and end_year != year:
                continue

            # Scale value
            if unit in ("USD", "shares"):
                value = entry["val"] / 1_000_000
            else:
                value = entry["val"]

            prev = annual_by_year.get(year)
            # Keep entry with the longest duration, just in case multiple exist
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
            if label not in balance_sheet_data[category]:
                balance_sheet_data[category][label] = {}
            for year, info in sorted(annual_by_year.items()):
                balance_sheet_data[category][label][year] = info["value"]
                print(
                    f"  Year: {year}, Form: {info['form']}, "
                    f"Frame: {info['frame']}, qtrs: {info['qtrs']}, "
                    f"Start: {info['start']}, End: {info['end']}, "
                    f"Duration: {info['duration_days']} days, "
                    f"Value (millions if USD/shares): {info['value']}"
                )
        else:
            print("  No annual-worthy entries found for this tag/unit in the chosen year range.")

    return balance_sheet_data

def create_dataframe(balance_data):
    years = set()
    for category, items in balance_data.items():
        for label, year_data in items.items():
            years.update(year_data.keys())
    years = sorted(years)

    category_order = [
        "Total Assets",
        "Current Assets",
        "Non-Current Assets",
        "Total Liabilities",
        "Current Liabilities",
        "Non-Current Liabilities",
        "Equity",
        "Total Liabilities and Equity",
    ]
    dfs = []

    for category in category_order:
        if category in balance_data and balance_data[category]:
            header_row = pd.DataFrame(
                [[f"**{category}**", ""] + [None] * len(years)],
                columns=["Category", "Item"] + years
            )
            category_data = []
            for label in sorted(balance_data[category].keys()):
                row = [label] + [balance_data[category][label].get(year, None) for year in years]
                category_data.append(row)
            category_df = pd.DataFrame(category_data, columns=["Item"] + years)
            dfs.extend([header_row, category_df])

    final_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame(columns=["Category", "Item"] + years)
    return final_df

def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    xbrl_data = get_xbrl_data()
    balance_data = extract_balance_sheet_data(xbrl_data)
    print("\nExtracted Balance Sheet Data (2014–2025, annual forms only, in millions):")
    for category, items in balance_data.items():
        print(f"\nCategory: {category}")
        for label, years in items.items():
            print(f"  {label}: {dict(sorted(years.items()))}")

    df = create_dataframe(balance_data)
    print("\nDataFrame:")
    print(df)

    # DYNAMIC FILENAME LOGIC
    dynamic_filename = f"{CIK}_balance_sheet.csv"
    save_to_csv(df, dynamic_filename)
