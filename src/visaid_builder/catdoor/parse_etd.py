"""
parse_etd.py

Structural/syntactic parsing logic for the editor text document (etd) field 
that is part of a catout entry.

The logic here assumes specific high level rules and conventions for 
structuring the data in the editor fields of cataids.

It assumes the vocabulary from `keys_catears`, and it uses the key-specific
or catear-specific functions there to validate values.  
"""

from .keys_catears import KEYS, CATEARS


def parse_etd( etd_text:str, asset_id:str = None ) -> list:
    """
    Top-level parsing logic of human edited/entered values.
    Takes a string of raw text as input.
    Returns a list of dictionaries.

    Typically, the returned list has just a single dictionary, but if the 
    user has used the "+++" syntax to multiplex the editor, there may be more
    than one.

    This function divides muliplexed editor text, uses a heuristic to choose
    the appropriate parsing, and then calls the appropriate parsing functions.
    It then returns a list of the results of each of those parsing functions.

    Keys in each dictionary returned:
       "problem" - boolean indicating any problem in parsing the etd data
       "etd_type" - the data convention (and type of parsing performed)
                    values: 'empty', 'keyed', 'chyron', 'catears-only', 'other'
       "chyron_data" - a dictionary of chyron data with 3 keys:
                    "name_as_written", "name_normalized", "person_attributes"
       "keyed_data" - a dictionary of whatever keyed data was in a section, 
                    with keys limited to values in `KEYS`
       "catear_data" - a dictionary of whatever catear keyed data was in a 
                    section, with keys limited to values in `CATEARS`
    """

    # allow multiple records per etd text
    etd_recs = []

    # divide multiplexed editor text and strip surrounding whitespace
    etd_secs = [ s.strip() for s in etd_text.split("\n+++") if s.strip() ]

    # for each section use the appropriate parser
    # The parser calls other functions as appropriate and reports errors
    for sec in etd_secs:

        lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
        ear_lines = [ l for l in lines if l[:2] == "^^" ]

        if not len(lines):
            # no lines -> empty section
            r = parse_sec_empty(sec, asset_id)

        elif lines[0][:1] == "*":
            # first line begins with asterisk -> keyed data section
            r = parse_sec_keyed(sec, asset_id)

        elif lines[0][:2] == "^^":
            # first line begins with catears -> ears-only section
            r = parse_sec_ears_only(sec, asset_id)

        elif ( len(lines) >= 2 and
               lines[0] not in ear_lines and
               lines[1] not in ear_lines ):
            # at least two non-catears lines -> chyron data section
            r = parse_sec_chyron(sec, asset_id)

        else:
            # none of the above -> other etd value
            r = parse_sec_other(sec, asset_id)

        if r:
            etd_recs.append(r)

    return etd_recs



def rec_problem( txt:str, asset_id:str = None, msg:str = None ) -> None:
    """
    Standard routine when encountering invalid etd data.
    For now, just prints out an informative error message.
    """
    print()
    if not msg:
        msg = "Invalid etd data"

    if asset_id:
        print(f"{asset_id}: {msg}")
    else:
        print(msg)

    print(f"```\n{txt}\n```\n")


############################################################################
# Section parsing functions
############################################################################

def parse_sec_empty( sec: str, asset_id:str = None ) -> dict:
    """
    Parse as empty.
    (I.e., no parsing)
    """

    rec_problem(sec, asset_id, msg="Empty etd section")

    r = {}
    r["problem"] = True
    r["etd_type"] = "empty"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = {}
    return r



def parse_sec_keyed( sec: str, asset_id:str = None ) -> dict:
    """
    Parse bullet list lines as key-value pairs, with a list of values
    for each key.

    Parse catears lines as catear key-value pairs.
    Catears in the values of keyed data lines are not handled here
    and are left to whatever is parsing values.
    """
    problem = False

    # get the non-empty lines
    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]

    # any line beginning with ^^ is an ears line
    ear_lines = [ l for l in lines if l[:2] == "^^" ]

    # key lines start with an *
    # key lines have colon at least one char after the *
    # key lines have their first space after the colon
    key_lines = [ l for l in lines if 
                  ( l[:1] == "*" and 
                    l.find(":") >= 2 and
                    ( l.find(" ") > l.find(":") or l.find(" ") == -1 ) ) ]

    bad_lines = [ l for l in lines if l not in (ear_lines + key_lines) ]

    if bad_lines or not key_lines:
        rec_problem(sec, asset_id, "Invalid keyed information section")
        problem = True

    # Even if there are bad lines, we'll still go ahead and try to extract 
    # information from valid keyed info lines or catears lines
    # dictionaries of keyed data
    keyed_data, k_problem = parse_key_lines(key_lines, asset_id) 
    catear_data, ce_problem = parse_catear_lines(ear_lines, asset_id)

    if k_problem or ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "keyed"
    r["chyron_data"] = {}
    r["keyed_data"] = keyed_data
    r["catear_data"] = catear_data
    return r



def parse_sec_chyron( sec: str, asset_id:str = None ) -> dict:
    """
    Parse as chyron data.
    (i.e., KSL Chyron note-4 conventions)
    """
    problem = False

    # get the non-empty lines
    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]

    # any line beginning with ^^ is an ears line
    ear_lines = [ l for l in lines if l[:2] == "^^" ]

    # KSL Note-4 style lines are the lines that are not catear lines
    n4lines = [ l for l in lines if l not in ear_lines ]

    assert len(n4lines) >= 2, "Must have at least 2 note4-style lines for chyron sec"

    chyron_data = {}
    chyron_data["name_as_written"] = n4lines[0]
    chyron_data["name_normalized"] = n4lines[1]

    if len(n4lines) > 2:
        chyron_data["person_attributes"] = "; ".join(n4lines[2:])
    else:
        chyron_data["person_attributes"] = None

    for k in ["name_as_written", "name_normalized", "person_attributes" ]:
        if chyron_data[k] is not None and chyron_data[k].find("^^") != -1:
            rec_problem(sec, asset_id, "Catears in chyron data")
            problem = True
    
    if len(chyron_data["name_normalized"]) > len(chyron_data["name_as_written"]) + 2:
        rec_problem(sec, asset_id, "Normalized name suspiciously long")
        problem = True

    catear_data, ce_problem = parse_catear_lines(ear_lines, asset_id)
    if ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "chyron"
    r["chyron_data"] = chyron_data
    r["keyed_data"] = {}
    r["catear_data"] = catear_data
    return r



def parse_sec_ears_only( sec: str, asset_id:str = None ) -> dict:

    problem = False

    # get the non-empty lines
    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]

    # any line beginning with ^^ is an ears line
    ear_lines = [ l for l in lines if l[:2] == "^^" ]

    bad_lines = [ l for l in lines if l not in ear_lines ]

    if bad_lines:
        rec_problem(sec, asset_id, "Cat ears but then extra")
        problem = True

    catear_data, ce_problem = parse_catear_lines(ear_lines, asset_id)
    if ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "catears-only"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = catear_data
    return r



def parse_sec_other( sec: str, asset_id:str = None ) -> dict:

    # this kind of etd is invalid.
    rec_problem(sec, asset_id, "Invalid section")
    problem = True

    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
    ear_lines = [ l for l in lines if l[:2] == "^^" ]

    catear_data, ce_problem = parse_catear_lines(ear_lines, asset_id)
    if ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "other"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = catear_data
    return r


############################################################################
# Line parsing functions
############################################################################

def parse_key_lines ( lines:list, asset_id:str = None ) -> dict:
    """
    Takes a list of lines of text.
    Returns a dictionary where the keys are in the list of valid keys.
    The value of each key is a list of string values.
    """

    keyed_data = {}
    problem = False

    for l in lines:
        assert l[:1] == "*", "Key lines must begin with '*'"

        k = l[1:l.find(":")].strip()
        v = l[l.find(":")+1:].strip()

        # validate key itself
        if k not in KEYS:
            rec_problem(l, asset_id, "Invalid key")
            problem = True
        
        # Validate value by calling the key-specific function in the dispatch table
        # (We're just going to check for problems discovered.  We are not using any
        #  transformation peformed by the dispatch function.)
        elif KEYS[k]:
            ki = KEYS[k](v)
            if ki["problems"]:
                message = ". ".join(ki["problems"])
                rec_problem(l, asset_id, message)
                problem = True
            else:
                # Key and value are valid.
                if k in keyed_data:
                    # Keys are repeatable.  Accumulate a list of values.
                    keyed_data[k].append(v)
                else:
                    keyed_data[k] = [ v ]

    return keyed_data, problem



def parse_catear_lines ( lines:list, asset_id:str = None ) -> dict:
    """
    Takes a list of lines of text.
    Returns a dictionary where the keys are in the list of valid catears.
    The value of each key is a string value (not a list).
    """

    catear_data = {}
    problem = False

    for l in lines:
        assert l[:2] == "^^", "Cat ear line must begin with '^^'"

        catears = [ c.strip() for c in l.split("^^") if c.strip() ]

        if len(catears) > 1:
            # Should we allow more than one catear per line?  As of now, we do.  
            #print(f"***  MORE THAN ONE CATEAR ON A LINE *** {asset_id}")
            #print(l)
            pass

        for c in catears:
            invalid_catear = False

            # look for key-value catears
            if c.find(":") == 0:
                # Case: no earkey
                invalid_catear = True
            elif c.find(":") > 0:
                # Case: key-value-style earkey with colon
                # earkey is the substring up to colon, minus whitespace
                k = c[:c.find(":")].strip()
                if k:
                    # value is everything after the colon, minus whitespace
                    v = c[c.find(":")+1:].strip()
                else:
                    # key is empty string
                    invalid_catear = True
            elif c.find(" ") != -1:
                # Case: text after catear key without colon
                # key is substring up to first space
                k = c[:c.find(" ")]
                # value is everything after
                v = c[c.find(" ")+1:].strip()
            else:
                # Case: non-key-value catear
                k = c
                v = ""
            
            if invalid_catear:
                rec_problem(l, asset_id, msg="Invalid catear line")
                problem = True
            else:
                if k not in CATEARS:
                    rec_problem(l, asset_id, msg="Invalid catear")
                    problem = True

                # Validate value by calling the catear-specific function in the dispatch table
                # (We're just going to check for problems discovered.  We are not using any
                #  transformation peformed by the dispatch function.)
                elif CATEARS[k]:
                    ki = CATEARS[k](v)
                    if ki["problems"]:
                        message = ". ".join(ki["problems"])
                        rec_problem(l, asset_id, message)
                        problem = True
                    else:
                        # Key and value are valid.
                        # Unlike keys, catears are not repeatable.
                        catear_data[k] = v 

    return catear_data, problem



