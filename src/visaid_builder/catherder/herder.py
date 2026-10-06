import argparse
from pathlib import Path

def main():
    cmd_description = 'Creates a fixer html file from a directory of (catout) files'

    parser = argparse.ArgumentParser(
        prog='catherder',
        description=cmd_description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("paths",
                        metavar="CATOUTPATH",
                        nargs="+", type=str,
                        help="Path to a single catout JSON file or a directory with many")

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path to the output file")

    catout_pattern = "*_catout*.json"
    catout_paths = []

    args = parser.parse_args()
    # this will be set to something sensible if exactly 1 input path is passed in.
    out_fname_morsel = ""

    for path_str in args.paths:
        input_path = Path(path_str)

        if not input_path.exists():
            print(f"Warning: '{path_str}' does not exist. Skipping...")
            continue

        elif input_path.is_file():
            # Check if the single file matches our required naming convention
            if input_path.match(catout_pattern):
                catout_paths.append(input_path)

                # Also set the output filename morsel if this the only input
                if len(args.paths) == 1:
                    out_fname_morsel = "".join(c if c.isalnum() else "_" for c in input_path.stem)

            else:
                print(f"Warning: File '{path_str}' does not match pattern {catout_pattern}. Skipping.")

        elif input_path.is_dir():
            # Find all matching files within the directory
            matches = list(input_path.glob(catout_pattern))
            catout_paths.extend(matches)

            # Also set the output filename morsel if this the only input
            if len(args.paths) == 1:
                out_fname_morsel = "".join(c if c.isalnum() else "_" for c in input_path.stem)

    # De-duplicate and sort for a clean list
    catout_paths = sorted(list(set(catout_paths)))

    if not catout_paths:
        print("No valid catout files specified.")
        print("Exiting.")
        return

if __name__ == "__main__":
    main()
