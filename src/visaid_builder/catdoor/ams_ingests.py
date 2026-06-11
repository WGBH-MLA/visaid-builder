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


def map_contrib_key_val( v:str, tp_time ) -> dict:

    d = keys_catears.KEYS["contrib"](v)

    tp_secs = f'{((int(tp_time))/1000):.3f}'

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
        "time_annotation": "Cataid Scene", 
        "affiliation": None,
        "affiliation_annotation": aff_ann,
        "contributor_role": role,
        "contributor_role_annotation": None
    }
    return contrib


def map_chyron_sec( r:dict ) -> dict:

    tp_secs = r["tp_time"] / 1000

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

    contrib = {
        "contributor": r["etd_data"]["chyron_data"]["name_normalized"], 
        "annotation": r["etd_data"]["chyron_data"]["name_as_written"],  
        "start_time": tp_secs, 
        "time_annotation": "Cataid Scene", 
        "affiliation": None, 
        "affiliation_annotation": aff_ann, 
        "contributor_role": role,
        "contributor_role_annotation": r["etd_data"]["chyron_data"]["person_attributes"]
    }
    return contrib



def make_full_contrib_ingest( outtable ):
    """
    This is the full contributor ingest format including data supported by 
    AMS2 updates in spring 2026.
    """

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
                if "contrib" in r["etd_data"]["keyed_data"]:
                    for v in r["etd_data"]["keyed_data"]["contrib"]:
                        contrib = map_contrib_key_val(v, r["tp_time"])
                        all_guid_contribs.append(contrib)

        # If there were any contrib entries for this guid, create list for it.
        if all_guid_contribs:        
            guid_contribs[guid] = []

            # Add just unique contributor entries
            # Uniqueness is determined by the normalized name, the role, and the role annotation.
            # (For this ingest, we do not want duplicates of that triple.)
            seen_uniques = set()

            for c in all_guid_contribs:
                c_uniqueness = (c["contributor"],c["contributor_role"],c["contributor_role_annotation"])
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

        min_contribution_cols = [
            "contributor", 
            "contributor_role"
        ]
        exp_contribution_cols = [
            "contributor", 
            "annotation", 
            "affiliation", 
            "contributor_role"
        ]
        all_contribution_cols = [
            "contributor", 
            "annotation", 
            "start_time", 
            "time_annotation", 
            "affiliation", 
            "affiliation_annotation", 
            "contributor_role",
            "contributor_role_annotation"
        ]
        contribution_cols = min_contribution_cols
        # contribution_cols = exp_contribution_cols
        # contribution_cols = all_contribution_cols

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


########################################################################
# DEPRECATED FUNCTIONS
########################################################################

# DEPRECATED
def parse_contrib_val( v:str ) -> (str, str, bool):
    # DEPRECATED
    
    # Find the role in parenetheses
    rolematch = re.search(r'\((.*?)\)', v)

    if rolematch:
        role = rolematch.group(1).strip()
        name = v.split("(")[0].strip()
    else:
        role = ""
        name = v.split("^")[0].strip()

    # Indicate whether there is a ^^home catear flag
    if v.find("^^home") != -1:
        home = True
    else:
        home = False

    return (name, role, home)


# DEPRECATED
def make_basic_contrib_ingest( catout_table ):
    """
    This is the original contributor ingest format, prior to updates to the 
    AMS2 data model.

    It captures only the normalized name (as the value of `Contribution.contributor`)
    and the role (as the value of `Contribution.contributor_role`).
    """
    # DEPRECATED

    # project down to just the important values
    data = [ { "asset_id": r["asset_id"], 
               "etd_type": r["etd_data"]["etd_type"],
               "chyron_data": r["etd_data"]["chyron_data"],
               "keyed_data": r["etd_data"]["keyed_data"],
               "catear_data": r["etd_data"]["catear_data"] }
              for r in catout_table ]

    # proceed one asset at a time
    # guids = list(set( [ r["asset_id"] for r in data ] ) )
    guids = list(dict.fromkeys( [ r["asset_id"] for r in data ] ) )

    # create a dictionary of contributor records for each asset
    guid_contribs = {}

    for guid in guids:
        all_guid_contribs = []
        for r in [r for r in data if r["asset_id"] == guid]:
            if r["etd_type"] == "chyron":
                if ("sens" not in r["catear_data"]):              
                    d = {}
                    d["name_normalized"] = r["chyron_data"]["name_normalized"]
                    d["role"] = ""
                    all_guid_contribs.append(d)
            elif r["etd_type"] == "keyed":
                if "contrib" in r["keyed_data"]:
                    # the value of each key is a list
                    for c in r["keyed_data"]["contrib"]:
                        d = {}
                        d["name_normalized"], d["role"], _ = parse_contrib_val(c)
                        all_guid_contribs.append(d)

        # get just unique contributors
        if all_guid_contribs:
            guid_contribs[guid] = []
            for c in all_guid_contribs:
                if c not in guid_contribs[guid]:
                    guid_contribs[guid].append(c)


    max_contribs = max( [ len(guid_contribs[guid]) for guid in guid_contribs ] ) 
    
    print(f"Will create contributor records for {len(guid_contribs)} items.")
    print(f"Max contributors per item: {max_contribs}")

    # create enough column headers for everyone from each item
    csv_header_row = ["Asset", "Asset.id"]
    for _ in range(max_contribs):
        csv_header_row += ["Contribution", "Contribution.contributor", "Contribution.contributor_role"]

    # first row is thea header
    csv_rows = [ csv_header_row ]

    # add rows for each asset
    contrib_recs = 0
    for guid in guid_contribs:
        row = ["", guid]
 
        for c in guid_contribs[guid]:
            row += [ "", c["name_normalized"], c["role"] ]
            contrib_recs += 1
 
        pad = max_contribs - len(guid_contribs[guid])
        for _ in range(pad):
            row += [ "", "", ""]

        csv_rows.append(row)

    print(f"Recorded {contrib_recs} contributor records.")

    # return value is a string of CSV text
    out_io = io.StringIO()
    csv.writer(out_io).writerows(csv_rows)
    csv_string = out_io.getvalue()
    return csv_string
