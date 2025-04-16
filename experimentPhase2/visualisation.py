import seaborn as sns
import matplotlib.pyplot as plt

import pandas as pd

# Load data
df = pd.read_csv("experiment-2-results.csv")
print(df.head())

from scipy.stats import pearsonr, spearmanr

def run_correlations(df, x_col, y_col):
    pearson_corr, pearson_p = pearsonr(df[x_col], df[y_col])
    spearman_corr, spearman_p = spearmanr(df[x_col], df[y_col])

    print(f"\n📊 Correlation between {x_col} and {y_col}:")
    print(f"Pearson r = {pearson_corr:.3f} (p = {pearson_p:.4f})")
    print(f"Spearman ρ = {spearman_corr:.3f} (p = {spearman_p:.4f})")

# Run for each hypothesis
run_correlations(df, "shared_vocab_score", "avg_cc")              # H1
run_correlations(df, "shared_vocab_score", "name_entropy")        # H2
run_correlations(df, "shared_vocab_score", "readability_score")   # H4

def plot_correlation(df, x, y):
    sns.lmplot(data=df, x=x, y=y, aspect=1.5)
    plt.title(f"{x} vs {y}")
    plt.show()

plot_correlation(df, "shared_vocab_score", "avg_cc")
plot_correlation(df, "shared_vocab_score", "pylint_score")
