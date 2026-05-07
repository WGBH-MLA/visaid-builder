"""
catout_door.py

Handles high-level processing out "catout" JSON files.

Also provides CLI interface for invoking processing.

Logic for parsing editor text from catouts is in separte module.

"""

import argparse
from pathlib import Path
import json

from . import catout_tables
from . import catout_ingests
from . import catout_parse_etd


def tablify_catouts( paths:list ) -> list:
    """
    Takes a list of filepaths to catout JSON files.

    Returns a table (list of dictionaries) with all target output fields.
    (Each list item corresponds to a single catout entry, allowing multiple 
     catout entries per frame if `+++` multiplexing is found.)

    This function operates at the aggregate level over lots of catouts.  

    This function works only at the level of explicit structure.  It calls
    a parsing function to interpret implicit structure.    

    Each list item is a dictionary with the following dkeys

    "asset_id"                - string: Asset ID
    "cataid_id"               - string: Cataid ID
    "cataid_ver"              - string: Cataid version string
    "cataloger"               - string: cataloger initials or name
    "export_date"             - string: ISO date
    "tp_time"                 - int:    time in milliseconds
    "tf_label"                - string: SWT scene label
    "tp_id"                   - string: MMIF TimePoint identifier
    "img_fname"               - string: KSL-style filename for the still image
    "img_data_uri"            - string: Base64 encoded image beginning "data:image/jpeg;base64,"
    "aid_text"                - string: Extracted text as appearing on cataid
    "etd_text"                - string: Edited text document from user
    "etd_data":               - dictionary   
    """

    catout_table = []

    # iterate through filepaths, accumulating rows
    for file_path in paths:
        catoutd = None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                catoutd = json.load(f)

        except json.JSONDecodeError as e:
            print(f"Error: '{file_path.name}' is not valid JSON. {e}")
        except PermissionError:
            print(f"Error: Permission denied when reading '{file_path.name}'.")
        except Exception as e:
            print(f"An unexpected error occurred with '{file_path.name}': {e}")            
    
        if catoutd:

            # each catout has multiple rows, one or more for each editor_item
            new_rows = []
            for ei in catoutd["editor_items"]:

                etd_recs = catout_parse_etd.parse_etd( ei["etd_text"] )

                # it is possible to have multiple etd records for a single editor_item
                for etd_rec in etd_recs:
                    r = {}

                    r["asset_id"]     = catoutd["asset_id"]
                    r["cataid_id"]    = catoutd["cataid_id"]
                    r["cataid_ver"]   = catoutd["cataid_ver"]
                    r["cataloger"]    = catoutd["cataloger"]
                    r["export_date"]  = catoutd["export_date"].split("T")[0]
                    r["tp_time"]      = int(ei["tp_time"])
                    r["tf_label"]     = ei["tf_label"]
                    r["tp_id"]        = ei["tp_id"]
                    r["img_fname"]    = ei["img_fname"]
                    r["aid_text"]     = ei["aid_text"]
                    r["etd_text"]     = ei["etd_text"]

                    r["etd_data"]     = etd_rec

                    r["img_data_uri"] = ei["img_data_uri"]

                    new_rows.append(r)

            catout_table += new_rows

    return catout_table


def main():

    parser = argparse.ArgumentParser(
        prog='catoutout',
        description='Outputs information from a collection of cataid output (catout) files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "paths", 
        type=str,
        metavar="CATOUTPATH",
        nargs="+",
        help="Path to a single catout JSON file or a directory with many")

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path to the output file")

    parser.add_argument(
        "-t", "--type",
        type=str,
        default="html-etd",
        help="Type of output to write")


    args = parser.parse_args()
    pattern = "*_catout*.json"
    catout_paths = []

    for path_str in args.paths:
        input_path = Path(path_str)

        if not input_path.exists():
            print(f"Warning: '{path_str}' does not exist. Skipping...")
            continue

        if input_path.is_file():
            # Check if the single file matches our required naming convention
            if input_path.match(pattern):
                catout_paths.append(input_path)
            else:
                print(f"Warning: File '{path_str}' does not match pattern {pattern}. Skipping.")
            
        elif input_path.is_dir():
            # Find all matching files within the directory
            matches = list(input_path.glob(pattern))
            catout_paths.extend(matches)

    # De-duplicate and sort for a clean list
    catout_paths = sorted(list(set(catout_paths)))

    # Create the quasi-tabular structure
    if catout_paths:
        catout_table = tablify_catouts( catout_paths )
    else:
        print("No valid catout files specified.  Exiting.")
        return

    # Choose the output type
    if args.type == "html-etd":
        out_str = catout_tables.make_etd_table(catout_table)
    elif args.type == "html-chy":
        out_str = catout_tables.make_chyron_review_table(catout_table)
    elif args.type == "html-exp":
        out_str = catout_tables.make_exp_table(catout_table)
    elif args.type == "html-key":
        out_str = catout_tables.make_keyed_data_table(catout_table)
    elif args.type[:7] == "csv-con":
        out_str = catout_ingests.make_basic_contrib_ingest(catout_table)

    if args.output:
        out_fname = args.output
    else:
        base = "catout_table"
        if args.type[:4] == "html":
            ext = ".html"
        elif args.type[:3] == "csv":
            ext = ".csv"
        else:
            ext = "txt"
        out_fname = base + ext

    if out_str:
        with open(out_fname, "w") as f:
            f.write(out_str)
            print(f"Wrote output file to to {out_fname}")
    else:
        print("No content to output.")


if __name__ == "__main__":
    main()
