"""
DataManager — Handles data downloads and live quote fetching via jugaad-data

This module integrates with jugaad-data for:
- EOD Bhavcopy downloads
- Live quotes via NSELive
- Corporate announcements
- F&O option chains
"""

from typing import Dict, List, Optional, Any
from datetime import date, datetime
from pathlib import Path
import threading


class DataManager:
    """
    Manages market data operations using jugaad-data.
    
    Features:
    - Download EOD bhavcopy data
    - Fetch live quotes via NSELive
    - Get corporate announcements
    - Fetch F&O option chains
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # NSELive instance for live data (lazy loaded)
        self._nse_live = None
    
    @property
    def nse_live(self):
        """Lazy load NSELive instance."""
        if self._nse_live is None:
            try:
                from jugaad_data.nse import NSELive
                self._nse_live = NSELive()
            except ImportError:
                print("Warning: jugaad-data not installed. Live data unavailable.")
                return None
        return self._nse_live
    
    # ========== EOD Data Downloads ==========
    
    def download_bhavcopy(self, trade_date: Optional[date] = None) -> bool:
        """
        Download daily bhavcopy for a specific date.
        
        Args:
            trade_date: Date to download. Defaults to today.
        
        Returns:
            True if successful, False otherwise.
        """
        if trade_date is None:
            trade_date = date.today()
        
        try:
            from jugaad_data.nse import bhavcopy_save
            bhavcopy_save(trade_date, str(self.data_dir))
            return True
        except Exception as e:
            print(f"Error downloading bhavcopy: {e}")
            return False
    
    def download_full_bhavcopy(self, trade_date: Optional[date] = None) -> bool:
        """
        Download full bhavcopy (includes delivery percentage).
        
        Args:
            trade_date: Date to download. Defaults to today.
        
        Returns:
            True if successful, False otherwise.
        """
        if trade_date is None:
            trade_date = date.today()
        
        try:
            from jugaad_data.nse import full_bhavcopy_save
            full_bhavcopy_save(trade_date, str(self.data_dir))
            return True
        except Exception as e:
            print(f"Error downloading full bhavcopy: {e}")
            return False
    
    def download_date_range(self, start_date: date, end_date: date) -> int:
        """
        Download bhavcopies for a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        
        Returns:
            Number of days successfully downloaded.
        """
        from datetime import timedelta
        
        count = 0
        current = start_date
        while current <= end_date:
            # Skip weekends (NSE closed)
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                if self.download_full_bhavcopy(current):
                    count += 1
            current += timedelta(days=1)
        
        return count
    
    def download_stock_history(
        self, 
        symbol: str, 
        from_date: date, 
        to_date: date,
        series: str = "EQ"
    ) -> bool:
        """
        Download historical stock data.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            from_date: Start date
            to_date: End date
            series: Series type (default "EQ")
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            from jugaad_data.nse import stock_csv
            output_path = self.data_dir / f"{symbol}.csv"
            stock_csv(symbol, from_date, to_date, series, str(output_path))
            return True
        except Exception as e:
            print(f"Error downloading {symbol} history: {e}")
            return False
    
    # ========== Live Quotes ==========
    
    def get_live_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch live quote for a symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with quote data or None if unavailable.
        """
        if self.nse_live is None:
            return None
        
        try:
            quote = self.nse_live.stock_quote(symbol)
            return quote
        except Exception as e:
            print(f"Error fetching live quote for {symbol}: {e}")
            return None
    
    def get_live_index(self, index_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch live index value.
        
        Args:
            index_name: Index name (e.g., "NIFTY 50", "INDIA VIX")
        
        Returns:
            Dictionary with index data or None if unavailable.
        """
        if self.nse_live is None:
            return None
        
        try:
            data = self.nse_live.live_index(index_name)
            return data
        except Exception as e:
            print(f"Error fetching index {index_name}: {e}")
            return None
    
    def get_all_indices(self) -> List[Dict[str, Any]]:
        """
        Fetch all market indices.
        
        Returns:
            List of index data dictionaries.
        """
        if self.nse_live is None:
            return []
        
        try:
            data = self.nse_live.all_indices()
            return data.get('data', [])
        except Exception as e:
            print(f"Error fetching all indices: {e}")
            return []
    
    # ========== Corporate Announcements ==========
    
    def get_corporate_announcements(
        self, 
        symbol: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch corporate announcements.
        
        Args:
            symbol: Filter by symbol (optional)
            from_date: Start date filter (optional)
            to_date: End date filter (optional)
        
        Returns:
            List of announcement dictionaries.
        """
        if self.nse_live is None:
            return []
        
        try:
            announcements = self.nse_live.corporate_announcements(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date
            )
            return announcements if isinstance(announcements, list) else []
        except Exception as e:
            print(f"Error fetching announcements: {e}")
            return []
    
    # ========== F&O Data ==========
    
    def get_option_chain(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch option chain for a symbol or index.
        
        Args:
            symbol: Symbol or index name
        
        Returns:
            Option chain data dictionary or None.
        """
        if self.nse_live is None:
            return None
        
        try:
            # Try equity option chain first
            chain = self.nse_live.equities_option_chain(symbol)
            if chain:
                return chain
            
            # Try index option chain
            chain = self.nse_live.index_option_chain(symbol)
            return chain
        except Exception as e:
            print(f"Error fetching option chain for {symbol}: {e}")
            return None
    
    def get_fno_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch F&O quote for a symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            F&O quote data dictionary or None.
        """
        if self.nse_live is None:
            return None
        
        try:
            quote = self.nse_live.stock_quote_fno(symbol)
            return quote
        except Exception as e:
            print(f"Error fetching F&O quote for {symbol}: {e}")
            return None
    
    def get_trade_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch trade info including block/bulk deals.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Trade info dictionary or None.
        """
        if self.nse_live is None:
            return None
        
        try:
            info = self.nse_live.trade_info(symbol)
            return info
        except Exception as e:
            print(f"Error fetching trade info for {symbol}: {e}")
            return None
    
    # ========== Market Status ==========
    
    def get_market_status(self) -> str:
        """
        Get current market status.
        
        Returns:
            Market status string.
        """
        if self.nse_live is None:
            return "UNKNOWN"
        
        try:
            status = self.nse_live.market_status()
            return status.get('marketState', 'UNKNOWN')
        except Exception as e:
            print(f"Error fetching market status: {e}")
            return "ERROR"
