if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Executes the compiled map style and prints resulting objects.')

    parser.add_argument('-b', '--bounds', dest='bounds',
        default='16.36,48.20,16.37,48.22',
        help='Process the map from the specified bounding box as min_lon,min_lat,max_lon,max_lat in WGS-84. (default: 16.36,48.20,16.37,48.22)'
    )

    args = parser.parse_args()

    bounds = args.bounds.split(',')
    if len(bounds) != 4:
        print("Error parsing bounds, expecting four numbers.")
        sys.exit(1)

    for i in pgmapcss_tmp(bounds):
        print(i)
