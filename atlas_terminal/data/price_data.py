"""
PriceData — In-memory price data container

Holds OHLCV data for all symbols in the universe.
Loaded from local CSV files (jugaad-data format).
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PriceData:
    """
    In-memory container for OHLCV price data.
    
    Attributes:
        data_dir: Directory containing CSV files (one per symbol)
        universe: List of symbols in the universe
        data: Dict mapping symbol -> DataFrame with OHLCV data
    """
    data_dir: Path
    universe: List[str] = field(default_factory=list)
    data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
    
    def load_symbol(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load price data for a single symbol from CSV."""
        csv_path = self.data_dir / f"{symbol}.csv"
        if not csv_path.exists():
            return None
        
        try:
            df = pd.read_csv(csv_path, parse_dates=['Date'])
            df.set_index('Date', inplace=True)
            # Ensure column names match expected format
            df.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Volume': 'Volume',
            }, inplace=True)
            self.data[symbol] = df
            return df
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return None
    
    def load_all(self, symbols: Optional[List[str]] = None) -> int:
        """
        Load all symbol data from the data directory.
        
        Args:
            symbols: Optional list of symbols to load. If None, loads all CSV files found.
        
        Returns:
            Number of symbols successfully loaded.
        """
        if symbols is None:
            # Discover all CSV files in data directory
            symbols = [f.stem for f in self.data_dir.glob("*.csv")]
        
        self.universe = symbols
        count = 0
        for symbol in symbols:
            if self.load_symbol(symbol) is not None:
                count += 1
        
        return count
    
    def get(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get price data for a symbol."""
        return self.data.get(symbol)
    
    def get_close_prices(self, symbol: str) -> Optional[pd.Series]:
        """Get close price series for a symbol."""
        df = self.data.get(symbol)
        if df is None:
            return None
        return df['Close']
    
    def get_ohlcv(self, symbol: str, days: int = 252) -> Optional[pd.DataFrame]:
        """
        Get OHLCV data for a symbol, limited to recent days.
        
        Args:
            symbol: Stock symbol
            days: Number of trading days to return (default ~1 year)
        
        Returns:
            DataFrame with OHLCV data or None if not found
        """
        df = self.data.get(symbol)
        if df is None:
            return None
        return df.tail(days)
    
    def symbols_loaded(self) -> List[str]:
        """Return list of symbols with loaded data."""
        return list(self.data.keys())
    
    def is_loaded(self, symbol: str) -> bool:
        """Check if a symbol's data is loaded."""
        return symbol in self.data
