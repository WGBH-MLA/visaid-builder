"""
html_tables.py

Functions for writing out quick and easy HTML tables for examining the data 
from a collection of catout files.
"""

from .keys_catears import KEYS, CATEARS
import json
from . import ams_ingests


HTML_CSS = """
<link rel="stylesheet" href="https://cdn.datatables.net/2.0.0/css/dataTables.dataTables.css">
<link rel="stylesheet" href="https://cdn.datatables.net/searchpanes/2.3.0/css/searchPanes.dataTables.css">
<link rel="stylesheet" href="https://cdn.datatables.net/select/2.0.0/css/select.dataTables.css">
<style>
    body{padding: 20px; font-family: sans-serif;}
    table{background-color: #E8E8E8;}
    td{border: 1px solid black;}
    th{border: 1px solid black;}
    .small{font-size: 0.7em;}
    div.fdata{width: 400px;}
    pre{white-space: pre-wrap; width: 300px;}
    img{height: 180px;}
    #catdoor{ max-width: 1200px; margin: 0 auto; }
</style>
"""

HTML_EXT_SCRIPTS = """
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/2.0.0/js/dataTables.js"></script>

<script src="https://cdn.datatables.net/searchpanes/2.3.0/js/dataTables.searchPanes.js"></script>
<script src="https://cdn.datatables.net/searchpanes/2.3.0/js/searchPanes.dataTables.js"></script>
<script src="https://cdn.datatables.net/select/2.0.0/js/dataTables.select.js"></script>
"""


############################################################################
# Helper functions
############################################################################


def stringify_keys( d:dict) -> str:
    s = ""

    keys_sorted = sorted([ k for k in d  if k[0]!="_" ])

    for k in keys_sorted:
        v = d[k]
        s += (k + " / ")
    
    if s:
        s = s[:-3]

    return s


def htmlify_catear_data( d:dict) -> str:
    s = ""

    keys_sorted = sorted([ k for k in d if k[0]!="_" ])

    for k in keys_sorted:
        v = d[k]
        s += ("<strong>^^" + k + "</strong>")
        if CATEARS[k](v)["raw_value"]:
            s += ": " + CATEARS[k](v)["raw_value"] 
        s += "<br>\n"    

    return s


def htmlify_attention( etd_data:dict ) -> str:
    s = ""
    if etd_data["problems"]:
        s += "problem +"
    if etd_data["alerts"]:
        s += "alert +"
    if s:
        s = s[:-2]
    return s


def htmlify_messages( etd_data:dict ) -> str:
    s = ""
    for p in etd_data["problems"]:
        s += p + "<br>"
    for a in etd_data["alerts"]:
        s += a + "<br>"
    return s


def htmlify_keyed_data( d:dict) -> str:
    s = ""

    keys_sorted = sorted([ k for k in d if k[0]!="_" ])

    for k in keys_sorted:
        for v in d[k]:
            # We want to print the raw value first.
            # We want to omit key names that begin with an underscore
            kv = "raw_value"
            s += f"<strong>{k}→ {kv}</strong>:\t{KEYS[k](v)[kv]}<br>\n"
            kv_sorted = sorted([ kv for kv in KEYS[k](v) if kv[0]!="_" and kv!="raw_value" ])
            for kv in kv_sorted:
                s += f"<strong>{k}→ {kv}</strong>:\t{KEYS[k](v)[kv]}<br>\n"
            s += f"<br>\n"
    return s


############################################################################
# Table creation functions
############################################################################

def make_etd_table( outtable ):

    fields = [ "asset ID",
               "cataloger",
               "export date",
               "time", 
               "still image",
               "etd type",
               "etd text", 
               "cat ears",
               "cat ear data",
               "to attend to",
               "message",
                ]

    html_css = HTML_CSS
    html_start = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<title>cat door</title>\n{html_css}\n</head>\n<body>\n"

    html_table_start = "<table id='catdoor'><thead><tr>\n"
    for f in fields:
        html_table_start += f"<th>{f}</th>"
    html_table_start += "\n</tr></thead>\n<tbody>"

    rows = ""

    for r in outtable:
        tr = "\n<tr>\n"
        tr += f"<td class='small'>{r['asset_id']}</td>"
        tr += f"<td>{r['cataloger']}</td>"
        tr += f"<td class='small'>{r['export_date']}</td>"
        tr += f"<td>{r['tp_time']}</td>"
        tr += f"<td><img src='{r['img_data_uri']}'></td>"
        tr += f"<td>{r['etd_data']['etd_type']}</td>"
        tr += f"<td><pre>{r['etd_text']}</pre></td>"
        tr += f"<td>{stringify_keys(r['etd_data']['catear_data'])}</td>"    
        tr += f"<td>{htmlify_catear_data(r['etd_data']['catear_data'])}</td>"
        tr += f"<td>{htmlify_attention(r['etd_data'])}</td>"
        tr += f"<td class='small'>{htmlify_messages(r['etd_data'])}</td>"
        tr += "\n</tr>\n"
        rows += tr

    html_table_end = "</tbody></table>"

    html_scripts = HTML_EXT_SCRIPTS + """
    <script>
        $(document).ready(function() {
            $('#catdoor').DataTable({
                pageLength: 100,
                // layout: defines where the facets (searchPanes) appear
                layout: {
                    top1: {
                        searchPanes: {
                            // Set to false so it only shows what we explicitly ask for in columnDefs
                            show: false
                        }
                    }
                },
                // configures the faceting behavior
                columnDefs: [
                    {
                        searchPanes: {
                            show: true
                        },
                        targets: [0, 1, 5, 7, 9]
                    },
                    {
                        searchPanes: {
                            show: false
                        },
                        targets: '_all' // Hide everything else explicitly
                    }
                ]
            });
        });
    </script>
    """

    html_end = "\n\n</body></html>"

    html_str = html_start + html_table_start + rows + html_table_end + html_scripts + html_end

    return html_str



def make_chyron_data_table( outtable ):

    fields  = [ "asset ID",
                "cataloger",
                "time", 
                "still image",
                "name as written",
                "name normalized",
                "person attributes",
                "cat ears",
                "cat ear data",
                 ]

    html_css = HTML_CSS
    html_start = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<title>cat door</title>\n{html_css}\n</head>\n<body>\n"

    html_table_start = "<table id='catdoor'><thead><tr>\n"
    for f in fields:
        html_table_start += f"<th>{f}</th>"
    html_table_start += "\n</tr></thead>\n<tbody>"

    rows = ""

    # filter down to just chyron sections
    chy_outtable = [ r for r in outtable if r["etd_data"]["etd_type"] == "chyron" ]

    for r in chy_outtable:
        tr = "\n<tr>\n"
        tr += f"<td class='small'>{r['asset_id']}</td>"
        tr += f"<td>{r['cataloger']}</td>"
        tr += f"<td>{r['tp_time']}</td>"
        tr += f"<td><img src='{r['img_data_uri']}'></td>"
        for f in ["name_as_written","name_normalized","person_attributes"]:
            val = r['etd_data']['chyron_data'][f]
            tr += f"<td>{val if val is not None else ''}</td>"
        tr += f"<td>{stringify_keys(r['etd_data']['catear_data'])}</td>"    
        tr += f"<td>{htmlify_catear_data(r['etd_data']['catear_data'])}</td>"
        tr += "\n</tr>\n"
        rows += tr

    html_table_end = "</tbody></table>"

    html_scripts = HTML_EXT_SCRIPTS + """
    <script>
        $(document).ready(function() {
            $('#catdoor').DataTable({
                pageLength: 100,
                // layout: defines where the facets (searchPanes) appear
                layout: {
                    top1: {
                        searchPanes: {
                            // Set to false so it only shows what we explicitly ask for in columnDefs
                            show: false
                        }
                    }
                },
                // configures the faceting behavior
                columnDefs: [
                    {
                        searchPanes: {
                            show: true
                        },
                        targets: [0, 1, 5, 6, 7]
                    },
                    {
                        searchPanes: {
                            show: false
                        },
                        targets: '_all' // Hide everything else explicitly
                    }
                ]
            });
        });
    </script>
    """

    html_end = "\n\n</body></html>"

    html_str = html_start + html_table_start + rows + html_table_end + html_scripts + html_end

    return html_str



def make_keyed_data_table( outtable ):

    fields = [ "asset ID",
               "cataloger",
               "time", 
               "still image",
               "keys",
               "keyed_data",
               "cat ears",
               "cat ear data",
                ]

    html_css = HTML_CSS
    html_start = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<title>cat door</title>\n{html_css}\n</head>\n<body>\n"

    html_table_start = "<table id='catdoor'><thead><tr>\n"
    for f in fields:
        html_table_start += f"<th>{f}</th>"
    html_table_start += "\n</tr></thead>\n<tbody>"

    rows = ""

    # filter down to just keyed sections
    k_outtable = [ r for r in outtable if r["etd_data"]["etd_type"] == "keyed" ]

    for r in k_outtable:
        tr = "\n<tr>\n"
        tr += f"<td class='small'>{r['asset_id']}</td>"
        tr += f"<td>{r['cataloger']}</td>"
        tr += f"<td>{r['tp_time']}</td>"
        tr += f"<td><img src='{r['img_data_uri']}'></td>"
        tr += f"<td>{stringify_keys(r['etd_data']['keyed_data'])}</td>"
        tr += f"<td><div class='fdata'>{htmlify_keyed_data(r['etd_data']['keyed_data'])}</div></td>"
        tr += f"<td>{stringify_keys(r['etd_data']['catear_data'])}</td>"    
        tr += f"<td>{htmlify_catear_data(r['etd_data']['catear_data'])}</td>"
        tr += "\n</tr>\n"
        rows += tr

    html_table_end = "</tbody></table>"

    html_scripts = HTML_EXT_SCRIPTS + """
    <script>
        $(document).ready(function() {
            $('#catdoor').DataTable({
                pageLength: 100,
                // layout: defines where the facets (searchPanes) appear
                layout: {
                    top1: {
                        searchPanes: {
                            // Set to false so it only shows what we explicitly ask for in columnDefs
                            show: false
                        }
                    }
                },
                // configures the faceting behavior
                columnDefs: [
                    {
                        searchPanes: {
                            show: true
                        },
                        targets: [0, 1, 4, 6]
                    },
                    {
                        searchPanes: {
                            show: false
                        },
                        targets: '_all' // Hide everything else explicitly
                    }
                ]
            });
        });
    </script>
    """

    html_end = "\n\n</body></html>"

    html_str = html_start + html_table_start + rows + html_table_end + html_scripts + html_end

    return html_str


def make_contrib_ingest_table( outtable ):
    """
    This function makes a table that is intended to represent exactly the data that 
    would be ingested into the AMS.
    It also shows the image and raw editor text.
    """

    fields = [ 
        "id",
        "start-time",
        "(still image)",
        "(raw editor text)",
        "contributor (name normalized)",
        "annotation (name as written)",
        "contributor-role-annotation (attributes)",
        "contributor-role (role)",        
        "affiliation-annotation (team)",
        ]

    contrib_fields = [ 
        "contributor",
        "annotation",
        "contributor_role_annotation",
        "contributor_role",
        "affiliation_annotation",
        ]

    html_css = HTML_CSS
    html_start = f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n<title>cat door</title>\n{html_css}\n</head>\n<body>\n"

    html_table_start = "<table id='catdoor'><thead><tr>\n"
    for f in fields:
        html_table_start += f"<th>{f}</th>"
    html_table_start += "\n</tr></thead>\n<tbody>"

    guids = list(dict.fromkeys([r["asset_id"] for r in outtable]))
    
    # Data wrangling to get the contributor data   
    rows_data = []
    # Work guid-by-guid
    for guid in guids:
        asset_contribs = []
        # For each frame, check whether it has contributor data
        for r in [r for r in outtable if r["asset_id"] == guid]:
            if r["etd_data"]["etd_type"] == "chyron":
                if "sens" not in r["etd_data"]["catear_data"]:
                    # perform conversion to AMS data model structure
                    c = ams_ingests.map_chyron_sec(r)
                    c["tp_time"] = f'{((int(r["tp_time"]))/1000):.3f}'
                    c["img_data_uri"] = r["img_data_uri"]
                    c["etd_text"] = r["etd_text"]
                    c["asset_id"] = guid
                    asset_contribs.append(c)
            elif r["etd_data"]["etd_type"] == "keyed":
                if ("contrib" in r["etd_data"]["keyed_data"] and 
                    "sens" not in r["etd_data"]["catear_data"]
                    ):
                    for v in r["etd_data"]["keyed_data"]["contrib"]:
                        # perform conversion to AMS data model structure
                        c = ams_ingests.map_contrib_key_val(v, r["tp_time"])
                        c["tp_time"] = f'{((int(r["tp_time"]))/1000):.3f}'
                        c["img_data_uri"] = r["img_data_uri"]
                        c["etd_text"] = r["etd_text"]
                        c["asset_id"] = guid
                        asset_contribs.append(c)
                        
        # Add just unique contributor entries.
        # Uniqueness is determined fields listed in a global variable 
        unique_asset_contribs = []
        seen_uniques = set()
        for c in asset_contribs:
            c_uniqueness_l = [ c[k] for k in ams_ingests.CONTRIB_UNIQUENESS_COLS ] 
            c_uniqueness = tuple(c_uniqueness_l)
            if c_uniqueness not in seen_uniques:
                seen_uniques.add(c_uniqueness)
                unique_asset_contribs.append(c)
        
        rows_data.extend(unique_asset_contribs)

    rows = ""
    for c in rows_data:
        tr = "\n<tr>\n"
        tr += f"<td class='small'>{c['asset_id']}</td>"
        tr += f"<td>{c['tp_time']}</td>"
        tr += f"<td><img src='{c['img_data_uri']}'></td>"
        tr += f"<td><pre>{c['etd_text']}</pre></td>"
        for f in contrib_fields:
            val = c.get(f)
            tr += f"<td>{val if val is not None else ''}</td>"
        tr += "\n</tr>\n"
        rows += tr

    html_table_end = "</tbody></table>"

    html_scripts = HTML_EXT_SCRIPTS + """
    <script>
        $(document).ready(function() {
            $('#catdoor').DataTable({
                pageLength: 100,
                // layout: defines where the facets (searchPanes) appear
                layout: {
                    top1: {
                        searchPanes: {
                            // Set to false so it only shows what we explicitly ask for in columnDefs
                            show: false
                        }
                    }
                },
                // configures the faceting behavior
                columnDefs: [
                    {
                        searchPanes: {
                            show: true
                        },
                        targets: [0, 4, 6, 7, 8]
                    },
                    {
                        searchPanes: {
                            show: false
                        },
                        targets: '_all' // Hide everything else explicitly
                    }
                ]
            });
        });
    </script>
    """

    html_end = "\n\n</body></html>"

    html_str = html_start + html_table_start + rows + html_table_end + html_scripts + html_end

    return html_str


def make_etd_atn_table( outtable ):

    atn_outtable = [ r for r in outtable if r["etd_data"]["problems"] or r["etd_data"]["alerts"] ]
    
    return make_etd_table(atn_outtable)



def make_attention_table( outtable ):

    atn_outtable = [ r for r in outtable if r["etd_data"]["problems"] or r["etd_data"]["alerts"] ]
    
    return make_etd_table(atn_outtable)
