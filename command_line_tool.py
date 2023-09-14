import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "-o", "--output", help="path for the output CSV file", type=str
)

parser.add_argument(
    "-i", "--input", nargs=2, help="Run the digital twin of a player by inserting PlayerId and Authorization Token", type=(int, str)
)

parser.add_argument(
    "-t", "--time", help="time interval, in minutes, to check for new data and possibly get new results", type=int
)
