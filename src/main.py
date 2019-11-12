import argparse
from sleep_reader import SleepReader
from time_parser import TimeParser
from dynamoDB_API import tiredDB_API


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
    data = times.timeParsing()

    print(data)

    DB = tiredDB_API(args.course_key, args.email, data)
    DB.post()


if __name__ == "__main__":
    main()
