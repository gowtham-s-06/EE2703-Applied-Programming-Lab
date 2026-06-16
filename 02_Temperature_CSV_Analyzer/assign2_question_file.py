# Implement the functions defined below to form a useful
# set of library functions.  Sometimes also called
# an Application Programming Interface or API
import csv
import matplotlib.pyplot as plt


# The two functions below are given as useful examples to start with
def get_city_temperatures(filename, city_name):
    """
    Extract temperature data for a specific city from CSV file.

    Parameters:
    filename (str): Path to the CSV file
    city_name (str): Name of the city to extract data for

    Returns:
    dict: Dictionary mapping 'YYYY-MM' to temperature (float)
          Returns empty dict if city not found
    """
    temperature_data = {}

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Check if this row matches our city
            if row["City"] == city_name:
                # Extract year-month from date (format: 1849-01-01 -> 1849-01)
                date_str = row["dt"]
                year_month = date_str[:7]  # Take first 7 characters (YYYY-MM)

                # Get temperature, handle missing values
                temp_str = row["AverageTemperature"]
                if temp_str and temp_str.strip():  # Check if not empty
                    try:
                        temperature = float(temp_str)
                        temperature_data[year_month] = temperature
                    except ValueError:
                        # Skip rows with invalid temperature data
                        continue

    return temperature_data


def get_available_cities(filename, limit=None):
    """
    Get list of unique cities in the dataset.

    Parameters:
    filename (str): Path to the CSV file
    limit (int): Maximum number of cities to return (None for all)

    Returns:
    list: List of unique city names
    """
    cities = set()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cities.add(row["City"])
            if limit and len(cities) >= limit:
                break

    return sorted(list(cities))


# =============================================================================
# ASSIGNMENT: Build a Temperature Data API
# =============================================================================
# Students should implement these 5 functions to create a complete API


def find_temperature_extremes(filename, city_name):
    """
    Find the hottest and coldest months on record for a city.

    Parameters:
    filename (str): Path to the CSV file
    city_name (str): Name of the city

    Returns:
    dict: {
        'hottest': {'date': 'YYYY-MM', 'temperature': float},
        'coldest': {'date': 'YYYY-MM', 'temperature': float}
    }

    """
    pass


def get_seasonal_averages(filename, city_name, season):
    """
    Calculate average temperature for a specific season across all years.
    Never mind that Chennai only has Hot, Hotter and Hottest...

    Parameters:
    filename (str): Path to the CSV file
    city_name (str): Name of the city
    season (str): 'spring', 'summer', 'fall', or 'winter'

    Returns:
    dict: {
        'city': str,
        'season': str,
        'average_temperature': float
    }

    Assume: Spring = Mar,Apr,May; Summer = Jun,Jul,Aug;
          Fall = Sep,Oct,Nov; Winter = Dec,Jan,Feb
    """
    pass


def compare_decades(filename, city_name, decade1, decade2):
    """
    Compare average temperatures between two decades for a city.

    Parameters:
    filename (str): Path to the CSV file
    city_name (str): Name of the city
    decade1 (int): First decade (e.g., 1980 for 1980s)
    decade2 (int): Second decade (e.g., 2000 for 2000s)

    Returns:
    dict: {
        'city': str,
        'decade1': {'period': '1980s', 'avg_temp': float, 'data_points': int},
        'decade2': {'period': '2000s', 'avg_temp': float, 'data_points': int},
        'difference': float,
        'trend': str  # 'warming', 'cooling', or 'stable'
    }

    """
    pass


def find_similar_cities(filename, target_city, tolerance=2.0):
    """
    Find cities with similar average temperatures to the target city.

    Parameters:
    filename (str): Path to the CSV file
    target_city (str): Reference city name
    tolerance (float): Temperature difference threshold in °C

    Returns:
    dict: {
        'target_city': str,
        'target_avg_temp': float,
        'similar_cities': [
            {'city': str, 'country': str, 'avg_temp': float, 'difference': float}
        ],
        'tolerance': float
    }

    """
    pass


def get_temperature_trends(filename, city_name, window_size=5):
    """
    Calculate temperature trends using moving averages and identify patterns.

    Parameters:
    filename (str): Path to the CSV file
    city_name (str): Name of the city
    window_size (int): Number of years for moving average calculation

    Returns:
    dict: {
        'city': str,
        'raw_annual_data': {'YYYY': float},  # Annual averages
        'moving_averages': {'YYYY': float},  # Moving averages
        'trend_analysis': {
            'overall_slope': float,  # °C per year
            'warming_periods': [{'start': year, 'end': year, 'rate': float}],
            'cooling_periods': [{'start': year, 'end': year, 'rate': float}]
        }
    }

    """
    pass


def demo_plot(filename, city_name, mode=0):
    """
    Plots the average temperature of a given city using matplotlib
    If using the default mode (ie mode 0), it plots using annual average temperature
    If using mode = 1, it plots using centered moving averages with window size = 5
    Parameters:
    filename (str): Path to the CSV file
    city_name (str): Name of the city
    mode (int): Mode of operation (0 or 1)

    Returns:
    A plot of temperature vs years
    """

    if mode == 0:
        data = get_city_temperatures(filename, city_name)
        if not data:
            raise ValueError(f"No data found for {city_name}")
        # Convert monthly to yearly averages
        yearly_data = {}
        for ym, temp in data.items():
            year = ym[:4]
            if year not in yearly_data:
                yearly_data[year] = []
            yearly_data[year].append(temp)

        years = sorted(yearly_data.keys())
        yearly_avg = []
        for y in years:
            temps = yearly_data[y]
            yearly_avg.append(sum(temps) / len(temps))
    elif mode == 1:
        data_ma = get_temperature_trends(filename, city_name, 5)["moving_averages"]
        years, yearly_avg = list(data_ma.keys()), list(data_ma.values())
    else:
        raise ValueError("Invalid mode")
    # Simple plot
    plt.figure(figsize=(12, 6))
    plt.plot(years, yearly_avg, color="tab:red", label=f"{city_name} Avg Temp")
    plt.title(f"Yearly Average Temperature - {city_name}", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    step = 10  # 1 label every 10 years (but sometimes higher due to missing data)
    # Show only some year labels (every 10th year)
    plt.xticks(
        ticks=range(0, len(years), step),
        labels=[years[i] for i in range(0, len(years), step)],
        rotation=45,  # Rotate the label by 45 degrees
        fontsize=10,
    )

    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.show()


# =============================================================================
# TESTING CODE
# =============================================================================


def test_api_functions():
    """
    Test all API functions with sample data.
    """
    filename = "GlobalLandTemperaturesByMajorCity.csv"
    test_city = "Madras"

    print("Testing Temperature Data API")
    print("=" * 40)

    # Test basic function
    temps = get_city_temperatures(filename, test_city)
    print(f"Basic function: Found {len(temps)} temperature records")

    # Test extremes
    extremes = find_temperature_extremes(filename, test_city)
    print(f"Extremes: Hottest = {extremes['hottest']['temperature']}°C")

    # Test seasonal averages
    summer_avg = get_seasonal_averages(filename, test_city, "summer")
    print(f"Seasonal: Summer average = {summer_avg['average_temperature']:.1f}°C")

    # Test decade comparison
    comparison = compare_decades(filename, test_city, 1980, 2000)
    print(f"Decades: Temperature change = {comparison['difference']:.2f}°C")

    # Test similar cities
    similar = find_similar_cities(filename, test_city, tolerance=3.0)
    print(f"Similar cities: Found {len(similar['similar_cities'])} matches")

    # Test trends
    trends = get_temperature_trends(filename, test_city)
    print(
        f"Trends: Overall slope = {trends['trend_analysis']['overall_slope']:.4f}°C/year"
    )


if __name__ == "__main__":
    test_api_functions()
