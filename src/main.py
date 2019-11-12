import argparse
from sleep_reader import SleepReader
from time_parser import TimeParser
from dynamoDB_API import dynamoDB_API


def main():
    parser = argparse.ArgumentParser(description='Sleep time check program')
    parser.add_argument('course_key', type=str, help="Input course_key")
    parser.add_argument('email', type=str, help="Input email")
    args = parser.parse_args()

    sleep_reader = SleepReader()
    sleep_reader.run()
    sleep_times = sleep_reader.getSleepTime()

    times = TimeParser(sleep_times)
    times.calculateNextDay()
    times.calculateDupTime()
    times.timeParsing()
    data = times.getTime()

    


if __name__ == "__main__":
    main()
