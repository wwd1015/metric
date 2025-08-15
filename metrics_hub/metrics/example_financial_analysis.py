"""
Example Financial Analysis Metric

This demonstrates the rich output capabilities of Metrics Hub including
DataFrames, interactive Plotly visualizations, and summary statistics.

Generated using the metrics-hub scaffolding system.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from metrics_hub import register_metric
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@register_metric("example_financial_analysis")
def calculate_financial_analysis(
    num_assets: int = 5,
    time_periods: int = 252,
    volatility: float = 0.2,
    start_value: float = 100.0
) -> Dict[str, Any]:
    """
    Example financial analysis with rich outputs including DataFrames and interactive charts.
    
    This metric demonstrates the capability to return multiple output types:
    - DataFrames for tabular data
    - Plotly charts for interactive visualizations  
    - Summary statistics as structured data
    
    Args:
        num_assets: Number of assets to simulate
        time_periods: Number of time periods (default: 252 for 1 year daily)
        volatility: Asset volatility (default: 0.2 for 20% annual vol)
        start_value: Starting asset value (default: 100.0)
    
    Returns:
        Dict containing:
        - price_data: DataFrame with simulated price data
        - performance_chart: Interactive Plotly line chart
        - correlation_heatmap: Interactive correlation matrix
        - summary_stats: Key performance metrics
    """
    try:
        logger.info(f"Calculating financial analysis with {num_assets} assets over {time_periods} periods")
        
        # Input validation
        if num_assets <= 0 or num_assets > 20:
            raise ValueError("num_assets must be between 1 and 20")
        if time_periods <= 0 or time_periods > 1000:
            raise ValueError("time_periods must be between 1 and 1000")
        if volatility <= 0 or volatility > 1:
            raise ValueError("volatility must be between 0 and 1")
        
        # Generate synthetic financial data
        np.random.seed(42)  # For reproducible results
        
        # Create date range
        dates = pd.date_range(start='2023-01-01', periods=time_periods, freq='D')
        
        # Generate asset names
        asset_names = [f'Asset_{chr(65+i)}' for i in range(num_assets)]
        
        # Simulate price paths using geometric Brownian motion
        dt = 1/252  # Daily time step
        price_data = pd.DataFrame(index=dates, columns=asset_names)
        
        for asset in asset_names:
            # Random walk with drift
            returns = np.random.normal(0.05 * dt, volatility * np.sqrt(dt), time_periods)
            prices = [start_value]
            
            for i in range(1, time_periods):
                prices.append(prices[-1] * np.exp(returns[i]))
            
            price_data[asset] = prices
        
        # Reset index to make date a column for easier plotting
        price_data_reset = price_data.reset_index()
        price_data_reset.rename(columns={'index': 'date'}, inplace=True)
        
        # Create performance chart
        performance_chart = go.Figure()
        
        for asset in asset_names:
            performance_chart.add_trace(go.Scatter(
                x=price_data.index,
                y=price_data[asset],
                mode='lines',
                name=asset,
                hovertemplate=f'{asset}<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
            ))
        
        performance_chart.update_layout(
            title='Asset Price Performance Over Time',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        # Calculate returns for correlation analysis
        returns_data = price_data.pct_change().dropna()
        
        # Create correlation heatmap
        correlation_matrix = returns_data.corr()
        
        correlation_heatmap = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        correlation_heatmap.update_layout(
            title='Asset Return Correlation Matrix',
            template='plotly_white',
            height=500,
            width=500
        )
        
        # Calculate summary statistics
        final_prices = price_data.iloc[-1]
        total_returns = (final_prices / start_value - 1) * 100
        volatilities = returns_data.std() * np.sqrt(252) * 100  # Annualized volatility
        sharpe_ratios = (total_returns / volatilities) * np.sqrt(252)
        
        # Portfolio-level statistics
        equal_weight_portfolio = returns_data.mean(axis=1)
        portfolio_return = equal_weight_portfolio.mean() * 252 * 100  # Annualized
        portfolio_vol = equal_weight_portfolio.std() * np.sqrt(252) * 100
        portfolio_sharpe = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
        
        summary_stats = {
            'analysis_period': f"{dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}",
            'num_assets': num_assets,
            'time_periods': time_periods,
            'best_performer': total_returns.idxmax(),
            'best_return': float(total_returns.max()),
            'worst_performer': total_returns.idxmin(),
            'worst_return': float(total_returns.min()),
            'avg_return': float(total_returns.mean()),
            'avg_volatility': float(volatilities.mean()),
            'portfolio_return': float(portfolio_return),
            'portfolio_volatility': float(portfolio_vol),
            'portfolio_sharpe': float(portfolio_sharpe),
            'max_correlation': float(correlation_matrix.where(correlation_matrix != 1).max().max()),
            'min_correlation': float(correlation_matrix.where(correlation_matrix != 1).min().min())
        }
        
        # Create detailed statistics table
        stats_table = pd.DataFrame({
            'Asset': asset_names,
            'Final_Price': final_prices.round(2),
            'Total_Return_Pct': total_returns.round(2),
            'Annualized_Volatility_Pct': volatilities.round(2),
            'Sharpe_Ratio': sharpe_ratios.round(3)
        })
        
        logger.info(f"Successfully calculated financial analysis for {num_assets} assets")
        
        result = {
            'price_data': price_data_reset,           # 📊 Full price time series
            'performance_chart': performance_chart,   # 📈 Interactive price chart
            'correlation_heatmap': correlation_heatmap, # 🎯 Correlation visualization
            'statistics_table': stats_table,         # 📋 Summary statistics table
            'summary_metrics': summary_stats          # 📊 Key metrics summary
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to calculate financial analysis: {e}")
        raise RuntimeError(f"Financial analysis calculation failed: {e}") from e