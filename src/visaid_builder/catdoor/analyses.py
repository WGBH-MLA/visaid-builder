"""
analyses.py

Functions to provide transformations and anylses of catout data.
"""

def dump_full_text( outtable:list ) -> str:
    """
    Concatenate and dump full etd_text from the catout table.
    """
    outtext = ""

    for r in outtable:
        outtext += str(r["etd_text"]) + "\n"
    
    return outtext


def get_unique_lines( outtable:list ) -> list:
    """
    Return a list of unique lines of etd_text from the catout table.
    """

    full_text = dump_full_text( outtable )
    all_lines = full_text.split("\n")
    all_content_lines = [ l for l in all_lines if l.strip() ]
    deduped_lines = list(dict.fromkeys(all_content_lines))

    return deduped_lines


def dump_unique_lines( outtable:list ) -> str:
    """
    Concatenate and dump unique lines of etd_text from the catout table.
    """
    outtext = ""

    lines = get_unique_lines( outtable )

    for line in lines:
        outtext += line + "\n"

    return outtext