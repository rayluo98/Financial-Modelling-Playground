import os
import time
import csv
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from itertools import combinations
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
import matplotlib.pyplot as plt
import seaborn as sns


class PairTrading:

    def __init__(self):
        self.data = {}
        self.correlation_matrix = pd.DataFrame()

    def collect_tickers(self, folder_path):
        """Reads tickers from various CSV files and stores in separate csv file"""
        # TODO: Remove this function out of the class
        # List to hold all symbols
        symbols = []

        # Iterate over all CSV files in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.csv'):
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_csv(file_path)
                print(f"Accessed file: {file_name}")
                # Extract the 'Symbol' column
                if 'Symbol' in df.columns:
                    symbols.extend(df['Symbol'].tolist())

        # Remove duplicates and sort symbols
        unique_symbols = set(symbols)

        # Save the symbols to a new CSV file
        output_file = os.path.join(folder_path, "all_tickers.csv")
        pd.DataFrame(unique_symbols, columns=["Symbol"]).to_csv(output_file, index=False)

        print(f"Tickers saved to {output_file}")

    def fetch_yf_data(self, folder_path, file_name, output_file):
        """Fetches high-frequency data from Yahoo Finance in the last 60 days"""
        # TODO: Remove this function out of the class
        input_file = os.path.join(folder_path, file_name)
        if not os.path.exists(input_file):
            print(f"File not found: {input_file}")
            return

        try:
            tickers_df = pd.read_csv(input_file)
            if 'Symbol' not in tickers_df.columns:
                print("The CSV file must have a 'Symbol' column.")
                return
            tickers = tickers_df['Symbol'].tolist()
        except Exception as e:
            print(f"Symbol column does not exist in the input file: {e}")
            return

        # Initialize an empty DataFrame to store data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=59)
        output_folder = os.path.join(folder_path, output_file)
        if not os.path.exists(output_folder):
            print(f"File not found: {output_folder}")
            return

        # Fetch high-frequency data for each ticker
        for ticker in tickers:
            print(f"Fetching data for ticker: {ticker}")
            try:
                data = yf.download(
                    ticker,
                    interval='2m',
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    progress=False
                )
                if (data.empty):
                    print(f"No data was fetched for {ticker}")
                    continue
                output_file = os.path.join(output_folder, f"{ticker}.csv")
                data.to_csv(output_file)
                # Pause to avoid being blocked
                time.sleep(2)
            except Exception as e:
                print(f"Failed to fetch data for {ticker}: {e}")

    def count_lines(self, folder_path):
        # TODO: Remove this function out of the class
        line_counts = []

        # Traverse through the folder and process each CSV file
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r') as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    count = sum(1 for _ in reader)
                    line_counts.append(count)

        # Sort the list from largest to smallest
        line_counts.sort(reverse=True)

        # Get smallest numbers
        smallest = sorted(line_counts[-40:])

        # Calculate the 90th percentile
        tenth_percentile = np.percentile(line_counts, 10)

        return {
            "smallest": smallest,
            "ninetieth_percentile": tenth_percentile
        }

    def read_data(self, folder_path):
        """Reads and cleans all CSV files in the folder."""
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                # Read CSV
                file_path = os.path.join(folder_path, file_name)
                df = pd.read_csv(file_path)

                # Discard data with less than 1800 lines
                if len(df) < 1800:
                    continue

                # Default key as file name
                table_name = os.path.splitext(file_name)[0]

                # Clean Data
                df = df.drop(index=[0, 1]).reset_index(drop=True)
                df.rename(columns={"Price": "Datetime"}, inplace=True)

                # Store in the dictionary
                self.data[table_name] = df

    def get_dataframes(self, ticker):
        """Returns the processed DataFrame dictionary."""
        return self.data[ticker]

    def compute_log_return(self, ticker1, ticker2, col):
        # Extract the data for both tickers
        data1 = self.data[ticker1][["Datetime", col]]
        data2 = self.data[ticker2][["Datetime", col]]

        # Align data based on matching 'Datetime'
        aligned_data = pd.merge(data1, data2, on="Datetime", how="inner", suffixes=("_1", "_2"))
        aligned_data[f"{col}_1"] = pd.to_numeric(aligned_data[f"{col}_1"], errors="coerce")
        aligned_data[f"{col}_2"] = pd.to_numeric(aligned_data[f"{col}_2"], errors="coerce")
        # aligned_data.dropna(subset=[f"{col}_1", f"{col}_2"], inplace=True)
        aligned_data["log_return_1"] = np.log(aligned_data[f"{col}_1"] / aligned_data[f"{col}_1"].shift(1))
        aligned_data["log_return_2"] = np.log(aligned_data[f"{col}_2"] / aligned_data[f"{col}_2"].shift(1))
        aligned_data.dropna(subset=["log_return_1", "log_return_2"], inplace=True)

        return aligned_data

    def compute_correlation(self, ticker1, ticker2, col):
        log_return = self.compute_log_return(ticker1, ticker2, col)
        correlation = log_return["log_return_1"].corr(log_return["log_return_2"])
        return correlation

    def compute_all_correlations(self, col):
        """
        Computes pairwise correlations between all stock tickers
        and stores the results in a DataFrame.
        """
        tickers = list(self.data.keys())
        n = len(tickers)

        # Define the correlation matrix in data structure
        self.correlation_matrix = pd.DataFrame(index=tickers, columns=tickers)

        # Compute correlations for each pair
        for i in range(n):
            for j in range(i, n):
                ticker1, ticker2 = tickers[i], tickers[j]
                if ticker1 == ticker2:
                    self.correlation_matrix.loc[ticker1, ticker2] = 1.0
                else:
                    correlation = self.compute_correlation(ticker1, ticker2,col)
                    print(f'Correlation between {ticker1} and {ticker2} is: {correlation}')
                    self.correlation_matrix.loc[ticker1, ticker2] = correlation
                    self.correlation_matrix.loc[ticker2, ticker1] = correlation

        # Convert values to numeric
        self.correlation_matrix = self.correlation_matrix.astype(float)

    def get_high_correlations(self, threshold=0.8):
        correlations = []
        tickers = list(self.data.keys())

        # Compute correlations for all pairs
        for ticker1, ticker2 in combinations(tickers, 2):
            correlation = self.correlation_matrix.loc[ticker1, ticker2]
            if correlation >= threshold:
                correlations.append((ticker1, ticker2, correlation))
        return correlations

    def engle_granger_test(self, ticker1, ticker2, col):
        """Performs the Engle-Granger two-step cointegration test."""
        log_return = self.compute_log_return(ticker1, ticker2, col)
        score, p_value, crit_values = coint(log_return["log_return_1"], log_return["log_return_2"])
        return p_value, score, crit_values

    def compute_beta(self, log_return_1, log_return_2):
        """Computes beta as the slope of the regression of R1 on R2."""
        # Ensure inputs are pandas Series
        log_return_1 = pd.Series(log_return_1)
        log_return_2 = pd.Series(log_return_2)

        # Add intercept for the regression
        log_return_2_with_const = sm.add_constant(log_return_2)

        # Perform OLS regression & Find Beta
        model = sm.OLS(log_return_1, log_return_2_with_const).fit()
        beta = model.params.iloc[1]
        return beta

    def calculate_snr(self, spread):
        """Calculates signal-to-noise ratio for the spread."""
        # Fit a simple mean-reverting model: spread_t = alpha + beta * spread_t-1 + noise
        lagged_spread = spread.shift(1).dropna()
        model = sm.OLS(spread[1:], lagged_spread).fit()

        # Signal variance: Variance explained by the model
        signal_variance = np.var(model.fittedvalues)

        # Total variance: Variance of the actual spread
        total_variance = np.var(spread)

        snr = signal_variance / (total_variance - signal_variance)
        return snr

    # TODO: Check the statistical intuition of this method
    def calculate_half_life(self, spread):
        """
        Calculates the half-life of mean reversion for the spread.
        """
        lagged_spread = spread.shift(1).dropna()
        spread = spread.iloc[1:]
        # Fit AR(1) model: Spread_t = alpha + beta * Spread_t-1 + noise
        model = sm.OLS(spread, sm.add_constant(lagged_spread)).fit()
        beta = model.params.iloc[1]

        if beta <= 0:
            print("Warning: Beta <= 0, half-life calculation invalid.")
            return None

        # Calculate half-life
        half_life = -np.log(2) / np.log(beta)
        return half_life

    def calculate_spread_metrics(self, spread):
        """Calculates metrics for spread distribution tightness."""
        z_scores = (spread - spread.mean()) / spread.std()
        kurtosis = spread.kurtosis()
        return {
            "z_scores": z_scores,
            "kurtosis": kurtosis
        }

    def plot_spread_distribution(self, spread):
        """
        Plots the spread time series and its distribution.

        Args:
            spread (pd.Series): The time series spread.
        """
        # Create a figure with two subplots
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})

        # Plot the spread time series
        axes[0].plot(spread.index, spread, label="Spread", color="blue", linewidth=1)
        axes[0].axhline(spread.mean(), color="red", linestyle="--", linewidth=1, label="Mean")
        axes[0].set_title("Spread Time Series")
        axes[0].set_xlabel("Time")
        axes[0].set_ylabel("Spread Value")
        axes[0].legend()
        axes[0].grid(True)

        # Plot the spread distribution (histogram + KDE)
        sns.histplot(spread, kde=True, ax=axes[1], color="purple", bins=50)
        axes[1].set_title("Spread Distribution")
        axes[1].set_xlabel("Spread Value")
        axes[1].set_ylabel("Frequency")

        plt.tight_layout()
        plt.show()

    def adf_test(self, ticker1, ticker2, col):
        log_return = self.compute_log_return(ticker1, ticker2, col)
        # beta = 1
        beta = self.compute_beta(log_return["log_return_1"], log_return["log_return_2"])
        print(f'Beta: {beta}')
        # Compute the spread
        log_return["spread"] = log_return["log_return_1"] - beta * log_return["log_return_2"]
        log_return.dropna(subset=["spread"], inplace=True)
        # Perform the ADF test on the spread
        adf_result = adfuller(log_return["spread"])

        # TODO: Clean up this part & move out of this function
        snr = self.calculate_snr(log_return["spread"])
        print(f'SNR: {snr}')
        half_life = self.calculate_half_life(log_return["spread"])
        print(f'Half life: {half_life}')
        spread_metrics = self.calculate_spread_metrics(log_return["spread"])
        print(f"Spread Kurtosis: {spread_metrics['kurtosis']}")
        self.plot_spread_distribution(log_return["spread"])

        # Unpack the results
        adf_stat = adf_result[0]
        p_value = adf_result[1]
        crit_values = adf_result[4]
        result = {
            "ADF Statistic": adf_stat,
            "p-value": p_value,
            "Critical Values": crit_values
        }
        return result

    # TODO: Complete backtest function
    def backtest_pair_trading(self):
        return None


if __name__ == '__main__':
    pt = PairTrading()
    folder_path = '/Users/andyxu/Desktop/U-M/FIN 342/Project/Tickers'
    file_name = 'Tickers.csv'
    output_file = 'HF_Data_by_Volume'
    # pt.collect_tickers(folder_path)
    # pt.fetch_yf_data(folder_path, file_name, output_file)
    # result = pt.count_lines('/Users/andyxu/Desktop/U-M/FIN 342/Project/Tickers/HF_Data_by_Volume')
    # print("Smallest line counts:", result["smallest"])
    # print("90th percentile:", result["ninetieth_percentile"])
    pt.read_data('/Users/andyxu/Desktop/U-M/FIN 342/Project/Tickers/HF_Data_by_Volume')
    # print(pt.get_dataframes('IREN'))
    # pt.compute_all_correlations()
    # print(pt.get_high_correlations())

    ticker1 = "COF"
    ticker2 = "DFS"
    corr = pt.compute_correlation(ticker1, ticker2, "Adj Close")
    print(f'Correlation: {corr}')

    p_value, score, crit_values = pt.engle_granger_test(ticker1, ticker2, "Adj Close")
    print(f"P-Value: {p_value:.10f}")
    print("Test Statistic:", score)
    print("Critical Values:", crit_values)

    result = pt.adf_test(ticker1, ticker2, "Adj Close")
    print("ADF Statistic:", result["ADF Statistic"])
    print("p-value:", result["p-value"])
    print("Critical Values:", result["Critical Values"])
