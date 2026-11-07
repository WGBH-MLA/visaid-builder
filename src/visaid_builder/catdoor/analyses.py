"""
analyses.py

Functions to provide transformations and anylses of catout data.
"""

import re

def dump_unique_words( outtable:list ) -> str:
    """
    Return a list of unique lines of etd_text from the catout table.
    """
    full_text = dump_full_text( outtable )

    # grab raw words by splitting and excluding punctuation
    raw_words = re.findall(r'\b\w+\b', full_text)

    # omit any "words" that contain no alphabetical characters.
    real_words = [ w for w in raw_words if any(c.isalpha() for c in w) ]

    # convert all words to lower case
    real_words_uncased = [ w.lower() for w in real_words ]

    # ensure uniqueness and sort
    real_words_uncased_uq = list( set(real_words_uncased) )
    real_words_uncased_uq.sort()

    outtext = ""
    for w in real_words_uncased_uq:
        outtext += w + "\n"

    return outtext


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