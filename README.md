# CyberCosmos-Project

## Planet Orbit Calculator

This repository contains a Python script that calculates the orbital elements, coordinates, and barycenter of the planets in the Solar System. The script uses mathematical formulas and data to determine the positions of the planets at a given date and time, as well as the barycenter of the Solar System.

## Installation

To run the code, you need to install the following libraries using pip:

Copy code
```
pip install dash
pip install pandas
pip install plotly
```
## Usage

1. Clone the repository to your local machine.

2. Open the Python script `planet_orbit_calculator.py` in your preferred Python editor or IDE.

3. Modify the date and time values in the code to the desired values:

```python
d = 30  # Day
m = 5   # Month
y = 1999  # Year
horas = 19  # Hours
minutos = 0  # Minutes
```
Run the script.

The script will calculate the orbital elements and coordinates of the planets (Mercury, Venus, Earth, Mars, and Jupiter) at the specified date and time.

The calculated results will be displayed in the console and stored in two Pandas DataFrames: elementosOrbitaisdf (containing the orbital elements) and coordenadasdf (containing the coordinates).


## Contributing

Contributions to this repository are welcome. If you find any issues or want to add new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
