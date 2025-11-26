import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# CONFIGURATION
# ==========================================
CIK = "0001045810"
FILES = {
    'IS': f"{CIK}_Income_Statement.csv",
    'BS': f"{CIK}_balance_sheet.csv",
    'CF': f"{CIK}_Cashflow_statement.csv"
}

def clean_transpose(file_path, prefix):
    try:
        # Load data
        df = pd.read_csv(file_path)
        
        # 1. CLEANING: Remove 'Category' rows if they exist
        if 'Category' in df.columns: 
            df = df[df['Category'].isna()] # Keep only rows where Category is NaN
            df = df.drop(columns=['Category']) # FIX: Assign back to df
            
        # 2. TRANSPOSE logic (moved outside the 'if' block to be safe)
        if 'Item' in df.columns:
            df = df.set_index('Item')
        
        df_t = df.transpose()
        df_t.index.name = 'Year'

        # Convert index to integer (Year) and sort 
        # We use a try/except here in case the header contains text like "Period"
        try:
            df_t.index = df_t.index.astype(int) 
            df_t = df_t.sort_index()
        except ValueError:
            print(f"Note: Could not convert index to integer for {prefix}. Check year formatting.")

        # 3. PREFIX: Rename columns (e.g., "IS_Net Income")
        df_t.columns = [f"{prefix}_{col}" for col in df_t.columns]
        
        # Ensure all data is numeric
        df_t = df_t.apply(pd.to_numeric, errors='coerce')
        
        return df_t
    
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}. Please run your extraction scripts first.")
        return pd.DataFrame()

# ==========================================
# EXECUTION
# ==========================================

# 1. Load and Clean the 3 Statements
print("Processing Income Statement...")
df_is = clean_transpose(FILES['IS'], 'IS')

print("Processing Balance Sheet...")
df_bs = clean_transpose(FILES['BS'], 'BS')

print("Processing Cash Flow...")
df_cf = clean_transpose(FILES['CF'], 'CF')

# 2. MERGE into MASTER DataFrame
master_df = df_is.join(df_bs, how='outer').join(df_cf, how='outer')

# Helper function
def get_col(df, col_name):
    if col_name in df.columns:
        return df[col_name].fillna(0)
    else:
        # We silence the warning to avoid spamming, but return 0
        return 0

# ==========================================
# 3. CALCULATE RATIOS
# ==========================================

# IMPORTANT DEBUG STEP: 
# This prints your actual column names. If your ratios are 0, check this list!
print("\n--- AVAILABLE COLUMNS (Use these exact names in your formulas) ---")
# print(master_df.columns.tolist()) 
print("------------------------------------------------------------------\n")

# --- Profitability Ratios ---
master_df['Calc_Net_Margin'] = get_col(master_df, 'IS_Net Income (Loss)') / get_col(master_df, 'IS_Total Net Revenues')
master_df['Calc_ROE'] = get_col(master_df, 'IS_Net Income (Loss)') / get_col(master_df, "BS_Total stockholders' equity")

# --- Liquidity Ratios ---
master_df['Calc_Current_Ratio'] = get_col(master_df, 'BS_Total current assets') / get_col(master_df, 'BS_Total current liabilities')

# --- STRESS TEST CONFIGURATION ---
# UPDATE THESE NAMES based on what you see in the print output above!
# I have put standard guesses here, but your CSV might be different.
cash_col_name   = 'BS_Cash and cash equivalents'       # Check your CSV! Might be 'BS_CashAndCashEquivalentsAtCarryingValue'
receiv_col_name = 'BS_Accounts receivable, net'        # Check your CSV! Might be 'BS_AccountsReceivableNetCurrent'
secur_col_name  = 'BS_Marketable securities, current'  # Check your CSV! Might be 'BS_MarketableSecuritiesCurrent'
liab_col_name   = 'BS_Total current liabilities'       # Check your CSV! Might be 'BS_LiabilitiesCurrent'

# Load variables safely
cash      = get_col(master_df, cash_col_name)
receiv    = get_col(master_df, receiv_col_name)
securities = get_col(master_df, secur_col_name)
liabilities = get_col(master_df, liab_col_name)

# Quick Ratio Base
master_df['Calc_Quick_Ratio_Base'] = (cash + receiv + securities) / liabilities

# Scenario A: Marketable Securities drop by 10%
master_df['Calc_Stress_Quick_10pct'] = (cash + receiv + (securities * 0.90)) / liabilities

# Scenario B: Marketable Securities drop by 15%
master_df['Calc_Stress_Quick_15pct'] = (cash + receiv + (securities * 0.85)) / liabilities

# Scenario C: Marketable Securities drop by 25%
master_df['Calc_Stress_Quick_25pct'] = (cash + receiv + (securities * 0.75)) / liabilities

# --- Cash Flow Ratios ---
master_df['Calc_FCF'] = get_col(master_df, 'CF_Net cash provided by (used in) operating activities') - get_col(master_df, 'CF_Cash spent on assets more than 1 year')

# Save the Master File
master_df.to_csv(f"{CIK}_MASTER_ANALYSIS.csv")
print(f"Success! Master Analysis File saved as: {CIK}_MASTER_ANALYSIS.csv")

# Print a preview
print(master_df[['Calc_Net_Margin', 'Calc_Quick_Ratio_Base', 'Calc_Stress_Quick_25pct']].tail())