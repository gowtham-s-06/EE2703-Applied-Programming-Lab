import assign2 as api

filename = r"C:\Users\gowth\OneDrive\Documents\EE2703\Assignment_2\GlobalLandTemperaturesByMajorCity.csv"
# l=api.get_available_cities(r"C:\Users\gowth\OneDrive\Documents\EE2703\Assignment_2\GlobalLandTemperaturesByMajorCity.csv")
# print(len(l))
f = ["summer", "winter", "spring", "fall"]
# print(api.demo_plot(filename, "Bombay", 1))
city_name = "Madras"
# print(api.find_temperature_extremes(filename, city_name))
# print(api.get_seasonal_averages(filename, city_name, "winter"))
print(api.compare_decades(filename, city_name, 1830, 1830))
# print(api.find_similar_cities(filename, city_name))
# print(api.get_temperature_trends(filename, city_name))
# print(api.get_available_cities(filename))
# print(api.get_city_temperatures(filename, city_name))

# print(api.get_temperature_trends(filename, city_name, 7))

# print(api.find_temperature_extremes(filename, "M"))
