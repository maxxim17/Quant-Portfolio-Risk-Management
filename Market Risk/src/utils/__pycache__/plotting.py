import matplotlib.pyplot as plt


def plot_ewma_volatility(
    volatility,
    title="EWMA Volatility",
):
    """
    Plot EWMA volatility.
    """

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        volatility.index,
        volatility.values,
    )

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility")

    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig, ax




def plot_raw_vs_scaled_returns(
    raw_returns,
    scaled_returns,
    title="Raw Returns vs EWMA Scaled Returns",
):
    """
    Compare raw and volatility-scaled returns.
    """

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        raw_returns.index,
        raw_returns.values,
        label="Raw Returns",
    )

    ax.plot(
        scaled_returns.index,
        scaled_returns.values,
        label="EWMA Scaled Returns",
    )

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Return")

    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig, ax






def plot_var_comparison(
    historical_var,
    ewma_var,
    title="Historical VaR vs EWMA VaR",
):
    """
    Compare Historical VaR and EWMA VaR.
    """

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        historical_var.index,
        historical_var.values,
        label="Historical VaR",
    )

    ax.plot(
        ewma_var.index,
        ewma_var.values,
        label="EWMA VaR",
    )

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("VaR")

    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig, ax





def plot_var_exceptions(
    actual_losses,
    historical_var,
    ewma_var,
    title="VaR Exception Comparison",
):
    """
    Plot actual losses against both VaR models.
    """

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    ax.plot(
        actual_losses.index,
        actual_losses.values,
        label="Actual Loss",
    )

    ax.plot(
        historical_var.index,
        historical_var.values,
        label="Historical VaR",
    )

    ax.plot(
        ewma_var.index,
        ewma_var.values,
        label="EWMA VaR",
    )

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Loss / VaR")

    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig, ax









