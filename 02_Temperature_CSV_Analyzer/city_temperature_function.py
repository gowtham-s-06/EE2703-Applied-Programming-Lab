# Implement the functions defined below to form a useful
# set of library functions.  Sometimes also called
# an Application Programming Interface or API
import time
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
    temperatures = get_city_temperatures(filename, city_name)
    # If city is not found, we check here
    if temperatures == {}:
        raise ValueError(f"No data found for {city_name}")

    # Initialising max and min with first values
    max_date = min_date = next(iter(temperatures))
    max_temp = min_temp = temperatures[max_date]

    for i in temperatures:
        if (
            temperatures[i] > max_temp
        ):  # If candidate has higher temp. we make it as new max.
            max_temp = temperatures[i]
            max_date = i
        elif temperatures[i] < min_temp:
            min_temp = temperatures[i]
            min_date = i

    dict_result = {
        "hottest": {"date": max_date, "temperature": max_temp},
        "coldest": {"date": min_date, "temperature": min_temp},
    }
    return dict_result


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
    # If city is not found, we check here
    temperatures = get_city_temperatures(filename, city_name)
    if temperatures == {}:
        raise ValueError(f"No data found for {city_name}")

    average = count = 0

    # Defining seasons and checking if its valid
    if season == "summer":
        months = ["06", "07", "08"]
    elif season == "fall":
        months = ["09", "10", "11"]
    elif season == "winter":
        months = ["12", "01", "02"]
    elif season == "spring":
        months = ["03", "04", "05"]
    else:
        raise ValueError("Invalid season")

    for i in temperatures:
        if (
            i[5:] in months
        ):  # i = 'YYYY-MM' so we extract last 2 characters (months) ie from index 5
            average += temperatures[i]
            count += 1

    # If no data found for a particular season
    if count == 0:
        print(f"No data found for {season}")
        return 1
    else:
        average = average / count

    dict_result = {"city": city_name, "season": season, "average_temperature": average}
    return dict_result


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
    # If city is not found, we check here
    temperatures = get_city_temperatures(filename, city_name)
    if temperatures == {}:
        print("No data found")
        return 1

    # Checking if decade inputs are valid
    if decade1 % 10 != 0 or decade2 % 10 != 0:
        print("Invalid decade range.")
        return 1

    average_decade1 = count_decade1 = 0
    average_decade2 = count_decade2 = 0

    for i in temperatures:
        # i = 'YYYY-MM' We extract first 3 characters to check if they belong in required decade
        if int(i[:3]) == decade1 // 10:
            average_decade1 += temperatures[i]
            count_decade1 += 1

        elif int(i[:3]) == decade2 // 10:
            average_decade2 += temperatures[i]
            count_decade2 += 1

    # Checking if both decades have atleast 1 data point
    if count_decade1 == 0:
        print(f"No data found for {decade1}")
        average_decade1 = "NA"
        difference = trend = "NA"
    elif count_decade2 == 0:
        print(f"No data found for {decade2}")
        average_decade2 = "NA"
        difference = trend = "NA"
    else:
        average_decade1 = average_decade1 / count_decade1
        average_decade2 = average_decade2 / count_decade2
        difference = average_decade2 - average_decade1
        if difference > 0:
            trend = "warming"
        elif difference < 0:
            trend = "cooling"
        else:
            trend = "stable"

    result = {
        "city": city_name,
        "decade1": {
            "period": f"{decade1}s",
            "avg_temp": average_decade1,
            "data_points": count_decade1,
        },
        "decade2": {
            "period": f"{decade2}s",
            "avg_temp": average_decade2,
            "data_points": count_decade2,
        },
        "difference": difference,
        "trend": trend,  # 'warming', 'cooling', or 'stable'
    }
    if decade1 > decade2:
        result["difference"] *= -1
        if result["trend"] == "warming":
            result["trend"] = "cooling"
        elif result["trend"] == "cooling":
            result["trend"] = "warming"
    return result


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

    def load_city_data(filename):
        """
        Read CSV once and compute all cities' average temperature.

        Returns:
            dict: {
                city_name: {
                    "country": str,
                    "avg_temp": float
                }
            }
        """
        temp_sums = {}
        counts = {}
        city_country = {}

        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                city = row["City"]
                country = row["Country"]

                city_country[city] = country

                temp_str = row["AverageTemperature"]
                if (
                    temp_str and temp_str.strip()
                ):  # Checking if data point is actually present
                    try:
                        temp = float(temp_str)
                        if city not in temp_sums:
                            temp_sums[city] = 0.0
                            counts[city] = 0
                        temp_sums[city] += temp
                        counts[city] += 1
                    except ValueError:
                        continue

        # Compute averages
        result = {}
        for city in temp_sums:
            avg_temp = temp_sums[city] / counts[city]
            result[city] = {"country": city_country[city], "avg_temp": avg_temp}
        return result

    # Start of actual function
    # Load in data of all cities along with their average temperatures and countries
    city_data = load_city_data(filename)

    if target_city not in city_data:
        print(f"{target_city} not found in database")
        return 1

    target_avg_temp = city_data[target_city]["avg_temp"]
    target_country = city_data[target_city]["country"]

    similar = []
    # Iterate through list of all cities. Here info is a dictionary with average temperatures and countries
    for city, info in city_data.items():
        if city == target_city:
            continue  # If it is same as target city, we ignore that
        difference = info["avg_temp"] - target_avg_temp
        if abs(difference) < tolerance:
            similar.append(
                {
                    "city": city,
                    "country": info["country"],
                    "avg_temp": info["avg_temp"],
                    "difference": difference,
                }
            )

    return {
        "target_city": target_city,
        "target_country": target_country,
        "target_avg_temp": target_avg_temp,
        "similar_cities": similar,
        "tolerance": tolerance,
    }


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

    # Collect monthly data year wise for target city
    yearly_data = {}
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["City"] != city_name:
                continue
            temp_str = row["AverageTemperature"]
            if not temp_str or not temp_str.strip():
                continue
            try:
                temp = float(temp_str)
                year = row["dt"][:4]
                if year not in yearly_data:
                    yearly_data[year] = []
                yearly_data[year].append(temp)
            except ValueError:
                continue

    # Compute annual averages
    raw_annual_data = {}
    for year, temps in yearly_data.items():
        if temps:
            total = 0.0
            for t in temps:
                total += t
            raw_annual_data[year] = total / len(temps)

    # Sort years
    sorted_years = sorted(raw_annual_data.keys())
    annual_values = []
    for yr in sorted_years:
        annual_values.append(raw_annual_data[yr])

    # Compute centered moving averages (calendar-based)
    moving_averages = {}
    half_window = window_size // 2  # how many years before and after

    for i in range(len(sorted_years)):
        center_year = int(sorted_years[i])
        start_year = center_year - half_window
        end_year = center_year + half_window
        if window_size % 2 == 0:
            end_year -= 1

        # If not enough data on either side, skip
        if (
            str(start_year) not in raw_annual_data
            or str(end_year) not in raw_annual_data
        ):
            continue  # So we take a moving average only when we have start and end years with complete data
        total = 0.0
        count = 0
        for yr in range(start_year, end_year + 1):  # symmetric window
            yr_str = str(yr)
            if yr_str in raw_annual_data:
                total += raw_annual_data[yr_str]
                count += 1

        if count > 0:  # avoid division by zero
            moving_averages[sorted_years[i]] = total / count

    # Overall slope using regression formula ---
    years_numeric = []  # Years as numeric data (for x values)
    for y in sorted_years:
        years_numeric.append(int(y))
    temps = annual_values  # Temperatures (for y values)
    n = len(years_numeric)
    sum_x = sum(years_numeric)  # Σx
    sum_y = sum(temps)  # Σy
    sum_xy = 0  # Calculating Σx * Σy
    for i in range(n):
        sum_xy += years_numeric[i] * temps[i]
    sum_x2 = 0  # Calculating Σ(x^2)
    for x in years_numeric:
        sum_x2 += x * x
    # Regression formula is
    # Slope  = (n*Σ(xy) - Σx*Σy) / (n*Σ(x^2) - (Σx)^2)
    numerator = n * sum_xy - sum_x * sum_y
    denominator = n * sum_x2 - (sum_x**2)
    slope = numerator / denominator if denominator != 0 else 0.0

    # Identify warming/cooling periods
    warming_periods = []
    cooling_periods = []
    years, temps = [], []
    for i in moving_averages:
        years.append(int(i))
        temps.append(moving_averages[i])
    if len(years) > 1:
        start_year = years[0]
        prev_temp = temps[0]
        current_trend = None  # "warming" or "cooling"

        for i in range(1, len(years)):
            year = years[i]
            temp = temps[i]

            if temp > prev_temp:
                trend = "warming"
            elif temp < prev_temp:
                trend = "cooling"
            else:
                trend = current_trend  # flat years follow last trend

            if current_trend is None:
                current_trend = trend
                start_year = years[i - 1]

            elif trend != current_trend and trend is not None:
                # Close previous period
                end_year = years[i - 1]
                if end_year > start_year:
                    rate = (temps[i - 1] - temps[years.index(start_year)]) / (
                        end_year - start_year
                    )
                    if current_trend == "warming":
                        warming_periods.append(
                            {
                                "start": str(start_year),
                                "end": str(end_year),
                                "rate": rate,
                            }
                        )
                    elif current_trend == "cooling":
                        cooling_periods.append(
                            {
                                "start": str(start_year),
                                "end": str(end_year),
                                "rate": rate,
                            }
                        )

                # Start new trend
                start_year = years[i - 1]
                current_trend = trend

            prev_temp = temp

        # Close final trend
        end_year = years[-1]
        if current_trend is not None and end_year > start_year:
            rate = (temps[-1] - temps[years.index(start_year)]) / (
                end_year - start_year
            )
            if current_trend == "warming":
                warming_periods.append(
                    {"start": str(start_year), "end": str(end_year), "rate": rate}
                )
            elif current_trend == "cooling":
                cooling_periods.append(
                    {"start": str(start_year), "end": str(end_year), "rate": rate}
                )

    return {
        "city": city_name,
        "raw_annual_data": raw_annual_data,
        "moving_averages": moving_averages,
        "trend_analysis": {
            "overall_slope": slope,
            "warming_periods": warming_periods,
            "cooling_periods": cooling_periods,
        },
    }


import matplotlib.pyplot as plt
from collections import defaultdict


def demo_plot(filename, city_name):
    data = get_city_temperatures(filename, city_name)
    if not data:
        print(f"No data found for {city_name}")
        return

    # Convert monthly → yearly averages
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

    # Simple plot
    plt.figure(figsize=(12, 6))
    plt.plot(years, yearly_avg, color="tab:red", label=f"{city_name} Avg Temp")
    plt.title(f"Yearly Average Temperature - {city_name}", fontsize=14)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    step = 10
    # Show only some year labels (e.g. every 10th year)
    plt.xticks(
        ticks=range(0, len(years), step),
        labels=[years[i] for i in range(0, len(years), step)],
        rotation=45,
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
