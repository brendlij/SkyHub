"""Astronomy utilities for day/night determination."""

from datetime import datetime, timedelta
import ephem


class AstronomyService:
    """Calculates sunrise/sunset and determines day/night periods."""
    
    def __init__(self, latitude: float = 48.0, longitude: float = 16.0):
        """
        Initialize with location (default: Vienna).
        
        Args:
            latitude: Decimal degrees (positive = North)
            longitude: Decimal degrees (positive = East)
        """
        self.latitude = latitude
        self.longitude = longitude
    
    def get_sunrise_sunset(self, date: datetime) -> tuple[datetime, datetime]:
        """
        Get astronomical sunrise and sunset for a given date.
        
        Args:
            date: Date to calculate for (UTC)
            
        Returns:
            (sunrise_datetime, sunset_datetime) in UTC
        """
        observer = ephem.Observer()
        observer.lat = str(self.latitude)
        observer.lon = str(self.longitude)
        # Set to midnight UTC of the given day
        observer.date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        sun = ephem.Sun()
        
        # Get sunrise: find next rising after midnight
        sunrise = observer.next_rising(sun)
        sunrise_dt = ephem.Date(sunrise).datetime().replace(tzinfo=None)
        
        # Get sunset: move observer to just after sunrise, then find next setting
        observer.date = sunrise
        sunset = observer.next_setting(sun)
        sunset_dt = ephem.Date(sunset).datetime().replace(tzinfo=None)
        
        return sunrise_dt, sunset_dt
    
    def is_daytime(self, timestamp: datetime) -> bool:
        """
        Determine if a timestamp is during daytime or nighttime.
        
        Day: sunrise to sunset
        Night: sunset to next sunrise
        
        Args:
            timestamp: Datetime to check (UTC)
            
        Returns:
            True if daytime, False if nighttime
        """
        # Get sunrise/sunset for this date
        sunrise, sunset = self.get_sunrise_sunset(timestamp)
        
        # Check if timestamp is between sunrise and sunset
        if sunrise <= timestamp <= sunset:
            return True
        
        # If before sunrise today, check yesterday's sunset
        if timestamp < sunrise:
            yesterday_sunrise, yesterday_sunset = self.get_sunrise_sunset(
                timestamp - timedelta(days=1)
            )
            if yesterday_sunset <= timestamp:
                return False
        
        return False
    
    def get_session_date(self, timestamp: datetime) -> tuple[str, str]:
        """
        Get the date folder and day/night label.
        
        Night sessions span two calendar days:
        - Night from today 18:00 to tomorrow 06:00 = stored under today's folder
        
        Args:
            timestamp: Datetime to check (UTC)
            
        Returns:
            (date_folder, period) where date_folder is "YYYY-MM-DD"
            and period is "day" or "night"
        """
        is_day = self.is_daytime(timestamp)
        
        if is_day:
            # Daytime: use current date
            date_folder = timestamp.strftime("%Y-%m-%d")
            period = "day"
        else:
            # Nighttime: check if it's after local sunset (belongs to previous calendar day)
            date_for_check = timestamp.replace(hour=0, minute=0, second=0)
            sunrise, sunset = self.get_sunrise_sunset(date_for_check)
            
            if timestamp >= sunset:
                # After today's sunset: belongs to today's night folder
                date_folder = timestamp.strftime("%Y-%m-%d")
            else:
                # Before today's sunrise: belongs to yesterday's night folder
                date_folder = (timestamp - timedelta(days=1)).strftime("%Y-%m-%d")
            
            period = "night"
        
        return date_folder, period
