"""
parse_etd.py

Provides one public function: `parse_etd` 

Handeles structural/syntactic parsing logic for the editor text document 
(etd) field  that is part of a catout entry.

The parsing logic here assumes and encodes specific high level rules for 
structuring the data in the editor fields of cataids.

It assumes the vocabulary from the `keys_catears` module, and it uses the 
key-specific or catear-specific functions in that module to validate values.  
However, it does not restructure any of those values (which are left as 
strings).  Those functions may need to be called again by downstream 
consumers of the data that comes out of `parse_etd`.
"""

__all__ = ['parse_etd']

from .keys_catears import KEYS, CATEARS, CHYRON_SEC_CATEARS, GENERAL_CATEARS

def parse_etd( etd_text:str, asset_id:str = None ) -> list:
    """
    Top-level parsing logic of human edited/entered values.
    Takes a string of raw editor text as input.
    Divides it into sections, if the user used the `+++` seperator.
    Returns a list of dictionaries, one for each section.

    Typically, the returned list has just a single dictionary, but if the 
    user has used the "+++" separator to multiplex the editor, there may be more
    than one.

    This function divides muliplexed editor text, uses a heuristic to choose
    the appropriate parsing, and then calls the appropriate parsing functions.

    Keys in each dictionary returned:
       "problem" - boolean indicating any problem in parsing the etd data
       "etd_type" - the data convention (and type of parsing performed)
                    values: 'empty', 'keyed', 'chyron', 'catears-only', 'other'
       "chyron_data" - either an empty dict or a dict with 3 keys with string values:
                    "name_as_written", "name_normalized", "person_attributes"
       "keyed_data" - either an empty dict or a dict of whatever valid keyed data 
                    was in the editor text section.  The value for each valid key 
                    is structured as another dict which always includes keys, 
                    'raw_value' and 'problems', and other keys relevant to the key
                    entered in the editor.  
       "catear_data" - a dict (possibly empty) of whatever catear keyed data was in
                     a section (with keys limited to values in `CATEARS`)
    """

    # Multiple records per etd text
    # Each record is the structured data from a section
    etd_recs = []

    # Divide multiplexed editor text and strip surrounding whitespace
    etd_secs = [ s.strip() for s in etd_text.split("\n+++") if s.strip() ]

    # For each section, use the appropriate parser.
    # The parser calls other functions, as appropriate, and reports errors
    for sec in etd_secs:

        lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
        ear_lines = [ l for l in lines if l[:2] == "^^" ]

        if not len(lines):
            # no lines -> empty section
            r = _parse_sec_empty(sec, asset_id)

        elif lines[0][:1] == "*":
            # first line begins with asterisk -> keyed data section
            r = _parse_sec_keyed(sec, asset_id)

        elif lines[0][:2] == "^^":
            # first line begins with catears -> ears-only section
            r = _parse_sec_ears_only(sec, asset_id)

        elif ( len(lines) >= 2 and
               lines[0] not in ear_lines and
               lines[1] not in ear_lines ):
            # at least two non-catears lines -> chyron data section
            r = _parse_sec_chyron(sec, asset_id)

        else:
            # none of the above -> other etd value
            r = _parse_sec_other(sec, asset_id)

        if r:
            etd_recs.append(r)

    return etd_recs


############################################################################
# General diagnostic helper function
############################################################################

def _rec_problem( txt:str, asset_id:str = None, msg:str = None ) -> None:
    """
    Standard routine that should be called by other functions when 
    encountering invalid etd data.

    For now, just prints out an informative error message.
    """
    print()
    if not msg:
        msg = "Invalid etd data"

    if asset_id:
        print(f"Item `{asset_id}`; {msg}")
    else:
        print(f"{msg}:")

    print("   ```")
    for line in txt.splitlines():
        print(f"   {line}")
    print("   ```\n")


############################################################################
# Section parsing functions
############################################################################

def _parse_sec_empty( sec: str, asset_id:str = None ) -> dict:
    """
    Parse as empty.
    (I.e., no parsing)
    """

    _rec_problem(sec, asset_id, msg="Empty editor section")
    problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "empty"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = {}
    return r


def _parse_sec_other( sec: str, asset_id:str = None ) -> dict:


    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
    ear_lines = [ l for l in lines if l[:2] == "^^" ]

    catear_data, ce_problem = _parse_catear_lines(ear_lines, asset_id)
    if ce_problem:
        problem = True

    # this kind of etd is invalid.
    _rec_problem(sec, asset_id, "Skipping: Invalid section")
    problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "other"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = catear_data
    return r


def _parse_sec_ears_only( sec: str, asset_id:str = None ) -> dict:

    problem = False

    # get the non-empty lines
    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]

    # any line beginning with ^^ is an ears line
    ear_lines = [ l for l in lines if l[:2] == "^^" ]

    bad_lines = [ l for l in lines if l not in ear_lines ]

    if bad_lines:
        _rec_problem(sec, asset_id, "Warning: Ignoring extra text after catears")
        problem = True

    catear_data, ce_problem = _parse_catear_lines(ear_lines, asset_id)
    if ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "catears-only"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = catear_data
    return r


def _parse_sec_keyed( sec: str, asset_id:str = None ) -> dict:
    """
    Parse bullet list lines as key-value pairs, with a list of values
    for each key.

    Parse catears lines as catear key-value pairs.
    (Catears in the values of keyed data lines are not handled here
    and are left to the function that parses that key.)
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
        _rec_problem(sec, asset_id, "Warning: Skipping invalid lines in keyed information section")
        problem = True

    # Even if there are bad lines, we'll still go ahead and try to extract 
    # information from valid keyed info lines or catears lines
    # dictionaries of keyed data
    keyed_data, k_problem = _parse_key_lines(key_lines, asset_id) 
    catear_data, ce_problem = _parse_catear_lines(ear_lines, asset_id, etd_type='keyed')

    if k_problem or ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "keyed"
    r["chyron_data"] = {}
    r["keyed_data"] = keyed_data
    r["catear_data"] = catear_data
    return r



def _parse_sec_chyron( sec: str, asset_id:str = None ) -> dict:
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

    # Do some checks so we can output warnings
    for k in ["name_as_written", "name_normalized", "person_attributes" ]:
        if chyron_data[k] is not None and chyron_data[k].find("^^") != -1:
            _rec_problem(sec, asset_id, "Warning: Catears appearing in in chyron data lines")
            problem = True   
    if len(chyron_data["name_normalized"]) > len(chyron_data["name_as_written"]) + 2:
        _rec_problem(sec, asset_id, "Warning: Normalized name suspiciously long")
        problem = True
    if chyron_data["name_normalized"].find(",") == -1:
        _rec_problem(sec, asset_id, "Warning: Normalized name contains no comma")
        problem = True
    elif chyron_data["name_as_written"].find(chyron_data["name_normalized"].split(",")[0]) == -1:
        _rec_problem(sec, asset_id, "Warning: Name as written doesn't include normalized surname")
        problem = True


    catear_data, ce_problem = _parse_catear_lines(ear_lines, asset_id, etd_type="chyron")
    if ce_problem:
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "chyron"
    r["chyron_data"] = chyron_data
    r["keyed_data"] = {}
    r["catear_data"] = catear_data
    return r



############################################################################
# Line parsing functions
############################################################################

def _parse_key_lines ( lines:list, asset_id:str = None ) -> dict:
    """
    This function converts a list of keyed value lines (strings) into a dict
    of valid keys and a list of values.

    Takes a list of lines of text.
    Returns a dictionary where the keys are in the list of valid keys.
    The value of each key is a list of string values.
    Each string value is the (stripped) raw key text.

    Note that the functions that are the values in the KEYS dictionary 
    are called here only for validation of the data values.  Those functions
    may need to be called downstream again for structuring values.
    """

    keyed_data = {}
    problem = False

    for l in lines:
        assert l[:1] == "*", "Key lines must begin with '*'"

        k = l[1:l.find(":")].strip()
        v = l[l.find(":")+1:].strip()

        # validate key itself
        if k not in KEYS:
            _rec_problem(l, asset_id, f"Warning: Skipping invalid key '{k}'")
            problem = True
        
        # Validate value by calling the key-specific function in the dispatch table
        # (We're just going to check for problems discovered.  We are not using any
        #  transformation peformed by the dispatch function.)
        elif KEYS[k]:
            ki = KEYS[k](v)

            # register any problems
            if ki["problems"]:
                message = ". ".join(ki["problems"])
                _rec_problem(l, asset_id, message)
                problem = True
            else:
                # Record values only if there were no problems.
                if k in keyed_data:
                    # Keys are repeatable.  Accumulate a list of values.
                    keyed_data[k].append(v)
                else:
                    keyed_data[k] = [ v ]

    return keyed_data, problem



def _parse_catear_lines ( lines:list, 
                          asset_id:str = None,  
                          etd_type = None,
                          ) -> dict:
    """
    This function converts a list of catear lines (strings) into a dict
    of valid catear data.  

    Takes a list of lines of text.
    Returns a dictionary where the keys are in the list of valid catears, 
    and the value for each key is a string value (not a list). For catears 
    for which not value is supplied, the value is the empty string.

    Note that the functions that are the values in the CATEARS dictionary 
    are called here only for validation of the data values.  Those functions
    may need to be called downstream again for structuring values.
    """

    if etd_type == "chyron":
        catear_dict = CATEARS
    else:
        catear_dict = GENERAL_CATEARS

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
                _rec_problem(l, asset_id, msg="Warning: Skipping invalid cat ear line")
                problem = True
            else:
                if k not in catear_dict:
                    _rec_problem(l, asset_id, msg=f"Warning: Skipping cat ear not valid in editor type {etd_type}")
                    problem = True

                # Validate value by calling the catear-specific function in the dispatch table
                # (We're just going to check for problems discovered.  We are not using any
                #  transformation peformed by the dispatch function.)
                elif catear_dict[k]:
                    ki = catear_dict[k](v)
                    # register any problems
                    if ki["problems"]:
                        message = ". ".join(ki["problems"])
                        _rec_problem(l, asset_id, message)
                        problem = True
                    
                    # unlike keys, for catears we save the value even if there was a problem
                    catear_data[k] = v 

    return catear_data, problem



