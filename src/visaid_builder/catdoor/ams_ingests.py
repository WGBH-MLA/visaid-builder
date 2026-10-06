"""
ams_ingests.py

The functions support creation of CSV files with columns suitable for batch
ingest into AMS2.
"""

import re
import csv
import io

import pprint

from . import keys_catears

CONTRIB_UNIQUENESS_COLS = [ "contributor","annotation","contributor_role","contributor_role_annotation"]

############################################################################
# Functions for transforming string values into AMS data values
############################################################################

def convert_tp_time( tp_time:str ) -> str:
    """
    Converts millisecons (expressed as int or string) to fractional
    seconds expressed as a string.
    """
    tp_secs = f'{((int(tp_time))/1000):.3f}'

    return tp_secs


def map_contrib_key_val( v:str, tp_time ) -> dict:

    d = keys_catears.KEYS["contrib"](v)

    tp_secs = convert_tp_time(tp_time)

    if d["home"]:
        aff_ann = "Producing Organization"
    else:
        aff_ann = None

    if d["role"]:
        role = d["role"]
    else:
        role = "Appearing"

    contrib = {
        "contributor": d["name_normalized"],
        "annotation": None,
        "start_time": tp_secs,
        "time_annotation": "Cataid Appearance", 
        "affiliation": None,
        "affiliation_annotation": aff_ann,
        "contributor_role": role,
        "contributor_role_annotation": None
    }
    return contrib


def map_chyron_sec( r:dict ) -> dict:

    tp_secs = convert_tp_time(r["tp_time"])

    if "home" in r["etd_data"]["catear_data"]:
        aff_ann = "Producing Organization"
    else:
        aff_ann = None

    if "role" in r["etd_data"]["catear_data"]:
        # parse the role value
        d = keys_catears.CATEARS["role"]( r["etd_data"]["catear_data"]["role"] )
        role = d["role"]
    else:
        role = "Appearing"

    if "omit-attributes" in r["etd_data"]["catear_data"]:
        attributes = None
    else:
        attributes = r["etd_data"]["chyron_data"]["person_attributes"]

    contrib = {
        "contributor": r["etd_data"]["chyron_data"]["name_normalized"], 
        "annotation": r["etd_data"]["chyron_data"]["name_as_written"],  
        "start_time": tp_secs, 
        "time_annotation": "Cataid Appearance", 
        "affiliation": None, 
        "affiliation_annotation": aff_ann, 
        "contributor_role": role,
        "contributor_role_annotation": attributes,
    }
    return contrib


############################################################################
# Main functions for supporting ingest
############################################################################

def make_full_contrib_ingest( outtable, level='full' ):
    """
    This is the full contributor ingest format including data supported by 
    AMS2 updates in spring 2026.
    """

    # Establish detail level of data to be ingested
    basic_contribution_cols = [
        "contributor", 
        "contributor_role"
    ]
    exp_contribution_cols = [
        "contributor", 
        "annotation", 
        "affiliation", 
        "contributor_role"
    ]
    full_contribution_cols = [
        "contributor", 
        "annotation", 
        "start_time", 
        "time_annotation", 
        "affiliation", 
        "affiliation_annotation", 
        "contributor_role",
        "contributor_role_annotation"
    ]

    if level == 'full':
        contribution_cols = full_contribution_cols
    elif level == 'basic':
        contribution_cols = basic_contribution_cols
    elif level == 'exp':
        contribution_cols = exp_contribution_cols

    # proceed one asset at a time
    # guids = list(set( [ r["asset_id"] for r in outtable ] ) )
    guids = list(dict.fromkeys( [ r["asset_id"] for r in outtable ] ) )

    # create a dictionary where each asset is associated with a list of 
    # contributor records
    guid_contribs = {}

    for guid in guids:

        all_guid_contribs = []
        for r in [r for r in outtable if r["asset_id"] == guid]:

            if r["etd_data"]["etd_type"] == "chyron":
                if "sens" not in r["etd_data"]["catear_data"]:
                    contrib = map_chyron_sec(r)
                    all_guid_contribs.append(contrib)
    
            elif r["etd_data"]["etd_type"] == "keyed":
                if ("contrib" in r["etd_data"]["keyed_data"] and 
                    "sens" not in r["etd_data"]["catear_data"]
                    ):
                    for v in r["etd_data"]["keyed_data"]["contrib"]:
                        contrib = map_contrib_key_val(v, r["tp_time"])
                        all_guid_contribs.append(contrib)

        # If there were any contrib entries for this guid, create list for it.
        if all_guid_contribs:        
            guid_contribs[guid] = []

            # Add just unique contributor entries.
            # Uniqueness is determined fields listed in a global variable 
            # that are also fields used in this ingest.
            seen_uniques = set()
            for c in all_guid_contribs:
                c_uniqueness_l = [ c[k] for k in CONTRIB_UNIQUENESS_COLS 
                                   if k in contribution_cols ] 
                c_uniqueness = tuple(c_uniqueness_l)
                if c_uniqueness not in seen_uniques:
                    seen_uniques.add(c_uniqueness)
                    guid_contribs[guid].append(c)

    if not guid_contribs:
        print("No contributor records found.")
        return None

    else:
        max_contribs = max( [ len(guid_contribs[guid]) for guid in guid_contribs ] ) 
        
        print(f"Will create contributor records for {len(guid_contribs)} items.")
        print(f"Max contributors per item: {max_contribs}")

        # create enough column headers for everyone from each item
        csv_header_row = ["Asset", "Asset.id"]
        for _ in range(max_contribs):
            csv_header_row += ["Contribution"] + [ "Contribution."+col for col in contribution_cols ]

        # first row is thea header
        csv_rows = [ csv_header_row ]

        # add rows for each asset
        contrib_recs = 0
        for guid in guid_contribs:
            # ["Asset", "Asset.id"]
            row = ["", guid]
    
            # ["Contribution", ... ]
            for c in guid_contribs[guid]:
                row += [""] + [ c[col] for col in contribution_cols ]
                contrib_recs += 1
    
            # add extra cells in rows where there item had fewer than the max contribs
            pad = max_contribs - len(guid_contribs[guid])
            for _ in range(pad):
                row += [""] * (1 + len(contribution_cols))

            csv_rows.append(row)

        print(f"Recorded {contrib_recs} contributor records.")

        # return value is a string of CSV text
        out_io = io.StringIO()
        csv.writer(out_io).writerows(csv_rows)
        csv_string = out_io.getvalue()
        return csv_string


def make_basic_contrib_ingest( catout_table ):

    return make_full_contrib_ingest( catout_table, level='basic' )


