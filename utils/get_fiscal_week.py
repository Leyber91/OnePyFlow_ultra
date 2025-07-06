import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_fiscal_week(date: datetime):
    """
    Calculate a 'fiscal week' similarly to the original logic, BUT
    then subtract 1 from the final week number. If that result is 0,
    set it to 52. This matches the Excel formula:
       =IF((Galaxy!N1-1)=0,52,Galaxy!N1-1)
    """

    fiscal_year = date.year
    jan1 = datetime(fiscal_year, 1, 1)

    # If the date is somehow before Jan 1 (e.g., 12/31 of prior year),
    # adjust accordingly.
    if date < jan1:
        fiscal_year -= 1
        jan1 = datetime(fiscal_year, 1, 1)

    # Find first Sunday of the year
    jan1_weekday = jan1.weekday()  # Monday=0, Sunday=6
    days_until_sunday = (6 - jan1_weekday) % 7
    first_sunday = jan1 + timedelta(days=days_until_sunday)

    if date < first_sunday:
        # partial chunk from Jan 1 up to (not including) the first Sunday
        fiscal_week = 1
    else:
        # on or after the first Sunday => "Week 2" starts there
        delta_days = (date - first_sunday).days
        fiscal_week = (delta_days // 7) + 2

    # -- Match the Excel logic: subtract 1 from the computed week,
    #    if result is 0, set week to 52
    adjusted_week = fiscal_week - 1
    if adjusted_week == 0:
        adjusted_week = 52

    return fiscal_year, adjusted_week

