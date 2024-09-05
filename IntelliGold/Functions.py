from datetime import datetime
from dateutil.relativedelta import relativedelta

def findMissingMonths(dates):
    if not dates:
        # Handle empty input case
        return []
    
    # Convert date strings to datetime objects
    try:
        dateObjects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
    except ValueError:
        # Handle invalid date format
        raise ValueError("Dates must be in 'YYYY-MM-DD' format")
    
    # Determine today’s date
    today = datetime.today()
    
    # Check if all dates are within the current month
    all_in_current_month = all(dateObj.year == today.year and dateObj.month == today.month for dateObj in dateObjects)
    
    if all_in_current_month:
        return []
    
    # Handle case with multiple dates or one date
    oldestDate = min(dateObjects)
    
    # Prepare a set to hold all months between the oldest date and today
    allMonths = set()
    current = oldestDate
    while current <= today:
        allMonths.add(current.strftime('%Y-%m'))  # Add in YYYY-MM format
        current += relativedelta(months=1)
    
    existingMonths = set(date.strftime('%Y-%m') for date in dateObjects)
    
    if existingMonths == allMonths:
        # All months have dates, return empty list
        return []
    
    # Calculate missing months
    missingMonths = sorted(allMonths - existingMonths)
    
    # Format the missing months
    monthsDict = {}
    for month in missingMonths:
        dateObj = datetime.strptime(month + '-01', '%Y-%m-%d')
        monthName = dateObj.strftime('%B')  # Full month name
        year = dateObj.strftime('%Y')        # Full year
        if year not in monthsDict:
            monthsDict[year] = []
        monthsDict[year].append(monthName)
    
    years = list(monthsDict.keys())
    formattedMissingMonths = []
    
    if len(years) == 1:
        # All months in the same year
        formattedMissingMonths = [month for month in monthsDict[years[0]]]
    else:
        # Different years
        formattedMissingMonths = [f"{month}, {year}" for year in monthsDict for month in monthsDict[year]]
    
    return formattedMissingMonths

def formatDateToMonthYear(dateStr):
    # Parse the date string to a datetime object
    dateObj = datetime.strptime(dateStr, '%Y-%m-%d')
    
    # Format the date to the desired output
    formattedDate = dateObj.strftime('%B %Y')  # Full month name and year
    
    return formattedDate