import argparse
import logging
import random
import math
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Obfuscates geographic coordinates by adding random noise.")

    parser.add_argument("latitude", type=float, help="The latitude of the location.")
    parser.add_argument("longitude", type=float, help="The longitude of the location.")
    parser.add_argument("radius", type=float, help="The radius (in meters) within which to add noise.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging (DEBUG level)")
    parser.add_argument("-n", "--num-points", type=int, default=1, help="Number of obfuscated points to generate.")

    return parser

def add_noise_to_coordinates(latitude, longitude, radius_meters):
    """
    Adds random noise to geographic coordinates.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        radius_meters (float): The radius (in meters) within which to add noise.

    Returns:
        tuple: A tuple containing the obfuscated latitude and longitude.
    """
    try:
        # Input validation
        if not isinstance(latitude, (int, float)):
            raise TypeError("Latitude must be a number.")
        if not isinstance(longitude, (int, float)):
            raise TypeError("Longitude must be a number.")
        if not isinstance(radius_meters, (int, float)):
            raise TypeError("Radius must be a number.")
        if radius_meters < 0:
            raise ValueError("Radius must be a non-negative number.")


        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

        earth_radius = 6371000

        # Sample a point inside the disc, not on its rim: the radial
        # distance needs the square root of a uniform draw, otherwise
        # every point lands at exactly the requested radius, which is
        # itself a recognisable pattern. The old code also used
        # radius / earth_radius (a figure in radians) as if it were
        # degrees, so a 1000 m request actually moved a point about
        # 17 m at the equator.
        distance = radius_meters * math.sqrt(random.random())
        random_angle = random.uniform(0, 2 * math.pi)

        # Metres to degrees is not one scale for both axes: a degree of
        # longitude covers cos(latitude) times the ground distance of a
        # degree of latitude, so the longitude step is divided by that.
        delta_latitude = (distance * math.sin(random_angle) / earth_radius) * (180 / math.pi)
        delta_longitude = (distance * math.cos(random_angle)
                            / (earth_radius * math.cos(math.radians(latitude)))) * (180 / math.pi)

        return latitude + delta_latitude, longitude + delta_longitude

    except (TypeError, ValueError) as e:
        logging.error(f"Error during coordinate obfuscation: {e}")
        raise  # Re-raise the exception for handling in main()

def main():
    """
    Main function to parse arguments, add noise to coordinates, and print the result.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled.")

    if args.num_points < 1:
        logging.error("Number of points must be at least 1.")
        sys.exit(1)

    try:
        for _ in range(args.num_points):
            new_latitude, new_longitude = add_noise_to_coordinates(args.latitude, args.longitude, args.radius)
            print(f"Original Coordinates: Latitude={args.latitude}, Longitude={args.longitude}")
            print(f"Obfuscated Coordinates: Latitude={new_latitude}, Longitude={new_longitude}")
            print("-" * 30)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    """
    Entry point of the script.
    """
    main()