import os
import time
import re
from datetime import datetime
import pandas as pd
import yfinance as yf

# --- Global Configuration & Setup ---

# Reverted to the .NS format for Yahoo Finance
TICKERS = {
    "National Alum": "NATIONALUM.NS",
    "Adani Green": "ADANIGREEN.NS",
    "Devyani": "DEVYANI.NS",
    "Coal India": "COALINDIA.NS",
    "Adani Wilmar": "AWL.NS",
    "Rel Power": "RPOWER.NS",
    "SW Solar": "SWSOLAR.NS",
    "Adani Power": "ADANIPOWER.NS",
    "Jio Fin": "JIOFIN.NS",
    "Central Bank": "CENTRALBK.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Brookfield REIT": "BIRET.NS"
}


# --- Core Functions ---

def fetch_stock_data_yfinance(ticker, company_name, start_date, end_date):
    """
    Fetches historical OHLCV data for a single stock using yfinance.
    """
    print(f"Fetching data for {company_name} ({ticker})...")
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, auto_adjust=True)

        if data.empty:
            print(f"  - No data found for {company_name} for the given period.")
            return None

        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            print(f"  - Error: Missing one of the required columns for {company_name}")
            return None

        return data.reset_index()

    except Exception as e:
        print(f"  - An unexpected error occurred for {company_name}: {e}")
        return None


def save_data_csv(df, file_name, save_separate, output_folder):
    """
    Saves the DataFrame to a CSV file(s) inside the specified output folder.
    Can save a single combined file or separate files per stock.
    """
    if df.empty:
        print("\nNo data within the specified interval to save.")
        return

    # The directory is now created in main(), so we just use it.

    # --- Prepare the entire DataFrame for saving ---
    df_to_process = df.copy()
    numeric_cols = ['Open', 'High', 'Low', 'Close']
    df_to_process[numeric_cols] = df_to_process[numeric_cols].round(2)
    df_to_process['Date'] = pd.to_datetime(df_to_process['Date']).dt.date
    output_cols = ['Date', 'Year', 'Company', 'Open', 'High', 'Low', 'Close', 'Volume']
    df_to_process = df_to_process.reindex(columns=output_cols)

    if save_separate == 'y':
        print(f"\nSaving separate CSV files in '{output_folder}'...")
        for company_name, company_df in df_to_process.groupby('Company'):
            # Create a filesystem-safe name for the company
            safe_company_name = re.sub(r'\W+', '', company_name.replace(' ', '_'))
            separate_file_name = f"{file_name}_{safe_company_name}.csv"
            csv_path = os.path.join(output_folder, separate_file_name)

            try:
                company_df.to_csv(csv_path, index=False)
                print(f" - Saved data to {csv_path}")
            except Exception as e:
                print(f"\nError saving file {csv_path}: {e}")
    else:
        # Original logic for a single file
        csv_path = os.path.join(output_folder, f"{file_name}.csv")
        try:
            print(f"\nSaving combined data to {csv_path}...")
            df_to_process.to_csv(csv_path, index=False)
            print("CSV saved successfully.")
        except Exception as e:
            print(f"\nError saving CSV file: {e}")


def save_analysis(pivot_df, agg_results, file_name, output_folder):
    """
    Saves the analysis results to a text file inside a 'data' folder.
    """
    if pivot_df is None or agg_results is None:
        print("No analysis results to save.")
        return

    # The directory is now created in main()
    analysis_path = os.path.join(output_folder, f"{file_name}_analysis.txt")

    try:
        print(f"\nSaving analysis to {analysis_path}...")
        with open(analysis_path, 'w') as f:
            f.write("--- Interval Performance Analysis ---\n\n")
            f.write("Percentage Change (%) within Interval per Year:\n")
            f.write(pivot_df.to_string(float_format="%.2f%%"))
            f.write("\n\n--- Aggregate Results ---\n\n")
            f.write(agg_results.to_string(index=False, float_format="%.2f%%"))
        print("Analysis file saved successfully.")
    except Exception as e:
        print(f"\nError saving analysis file: {e}")


def perform_interval_analysis(full_df, interval):
    """
    Performs and displays interval-based performance analysis.
    Returns the results as DataFrames for saving.
    """
    print("\n--- Interval Performance Analysis ---")
    results = []
    interval_start, interval_end = interval

    for (company, year), group in full_df.groupby(['Company', 'Year']):
        start_date_str = f"{year}-{interval_start}"
        end_date_str = f"{year}-{interval_end}"
        interval_df = group[(group['Date'] >= start_date_str) & (group['Date'] <= end_date_str)]

        if len(interval_df) < 2:
            continue

        open_first_day = interval_df.iloc[0]['Open']
        close_last_day = interval_df.iloc[-1]['Close']
        if pd.isna(open_first_day) or open_first_day == 0:
            continue
        
        pct_change = ((close_last_day - open_first_day) / open_first_day) * 100
        results.append({'Company': company, 'Year': year, 'Pct_Change': pct_change})

    if not results:
        print("Could not compute analysis. Not enough data in the specified intervals.")
        return None, None

    results_df = pd.DataFrame(results)
    pivot_df = results_df.pivot(index='Year', columns='Company', values='Pct_Change')
    print("\nPercentage Change (%) within Interval per Year:")
    print(pivot_df.to_string(float_format="%.2f%%"))

    print("\n--- Aggregate Results ---")
    agg_results = results_df.groupby('Company')['Pct_Change'].agg(['mean']).reset_index()
    agg_results.rename(columns={'mean': 'Avg_Pct_Change'}, inplace=True)
    agg_results['Trend'] = agg_results['Avg_Pct_Change'].apply(lambda x: "Increased" if x > 0 else "Decreased")
    print(agg_results.to_string(index=False, float_format="%.2f%%"))
    
    return pivot_df, agg_results


def get_user_input():
    """
    Prompts the user for input parameters and validates them.
    """
    # Interval validation
    date_pattern = re.compile(r'^\d{2}-\d{2}$')
    while True:
        try:
            interval_str = input("Enter interval ('MM-DD','MM-DD') [e.g., 10-01,10-15]: ").strip()
            start, end = [d.strip() for d in interval_str.split(',')]
            if not date_pattern.match(start) or not date_pattern.match(end):
                raise ValueError("Format must be MM-DD.")
            datetime.strptime(f"2024-{start}", "%Y-%m-%d")
            datetime.strptime(f"2024-{end}", "%Y-%m-%d")
            if start > end:
                raise ValueError("Start date of interval cannot be after end date.")
            interval = (start, end)
            break
        except (ValueError, IndexError) as e:
            print(f"Invalid input. Please use 'MM-DD,MM-DD' format. Error: {e}")

    # Past years validation
    while True:
        try:
            past_years = int(input("Enter number of past years to fetch (e.g., 5): ").strip())
            if past_years > 0: break
            print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")
    
    # File name validation
    while True:
        file_name = input("Enter the base name for output files (e.g., indian_stock_data): ").strip()
        if file_name: break
        print("File name cannot be empty.")
    
    # Separate files validation
    while True:
        save_separate = input("\nSave a separate file for each stock? (y/n): ").lower().strip()
        if save_separate in ['y', 'n']:
            break
        print("Invalid input. Please enter 'y' or 'n'.")

    return interval, past_years, file_name, save_separate


def main():
    """
    Main function to orchestrate the data fetching, processing, and analysis.
    """
    print("--- Indian Stock Market Data Fetcher & Analyzer (Yahoo Finance) ---")
    interval, past_years, file_name, save_separate = get_user_input()

    # --- NEW: Create a unique, timestamped folder for this run ---
    run_timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_folder_path = os.path.join("data", f"run_{run_timestamp}")
    os.makedirs(output_folder_path, exist_ok=True)
    print(f"\nAll output files will be saved in: '{output_folder_path}'")
    # -----------------------------------------------------------------

    current_year = datetime.now().year
    start_date_dt = datetime(current_year - past_years, 1, 1)
    end_date_dt = datetime(current_year, 1, 1)

    print(f"\nConfiguration:")
    print(f" - Data Period: {start_date_dt.strftime('%Y-%m-%d')} to {end_date_dt.strftime('%Y-%m-%d')}")
    print(f" - Analysis Interval: {interval[0]} to {interval[1]}")
    print("-" * 20)

    all_stocks_data = []
    
    for company, ticker in TICKERS.items():
        data = fetch_stock_data_yfinance(ticker, company, start_date_dt, end_date_dt)
        
        if data is not None:
            data['Company'] = company
            data['Year'] = data['Date'].dt.year
            all_stocks_data.append(data)
        time.sleep(1)

    if not all_stocks_data:
        print("\nCould not fetch data for any stocks. Exiting.")
        return

    full_df = pd.concat(all_stocks_data, ignore_index=True)
    full_df = full_df[full_df['Year'] < current_year].copy()
    full_df.sort_values(by=['Company', 'Date'], inplace=True)

    print(f"\nFiltering all data to the interval: {interval[0]} to {interval[1]} for each year...")
    full_df['MonthDay'] = full_df['Date'].dt.strftime('%m-%d')
    interval_df = full_df[
        (full_df['MonthDay'] >= interval[0]) & (full_df['MonthDay'] <= interval[1])
    ].copy()
    interval_df.drop(columns=['MonthDay'], inplace=True)
    
    pivot_df, agg_results = None, None
    while True:
        do_analysis = input("\nDo you want interval performance analysis? (y/n): ").lower().strip()
        if do_analysis in ['y', 'n']: break
        print("Invalid input.")

    if do_analysis == 'y':
        pivot_df, agg_results = perform_interval_analysis(full_df, interval)

    # --- MODIFIED: Pass the new output folder path to the save functions ---
    save_data_csv(interval_df, file_name, save_separate, output_folder_path)

    if pivot_df is not None:
        save_analysis(pivot_df, agg_results, file_name, output_folder_path)

    print("\nProgram finished successfully.")


if __name__ == "__main__":
    main()


