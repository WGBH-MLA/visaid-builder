"""
parse_etd.py

Structural/syntactic parsing logic for the editor text document (etd) field 
that is part of a catout entry.

The logic here assumes specific high level rules and conventions for 
structuring the data in the editor fields of cataids.

It assumes the vocabulary from `keys_catears`, but it does not rely on 
semantic properties of terms in the vocab.
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

    Keys in the returned dictionary:
       "problem" - indicates any problem in parsing the etd data
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

    for sec in etd_secs:

        lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
        ears_lines = [ l for l in lines if l[:2] == "^^" ]

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
               lines[0] not in ears_lines and
               lines[1] not in ears_lines ):
            # at least two non-catears lines -> chyron data section
            r = parse_sec_chyron(sec, asset_id)

        else:
            # none of the above -> other etd value
            r = parse_sec_other(sec, asset_id)

        if r:
            etd_recs.append(r)

    return etd_recs



def parse_sec_empty( sec: str, asset_id:str = None ) -> dict:
    """
    Parse as empty.
    (I.e., no parsing)
    """

    rec_invalid_sec(l, asset_id, msg="Empty etd section")

    r = {}
    r["problem"] = True
    r["etd_type"] = "empty"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = {}

    return None



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

    ears_lines = [ l for l in lines if l[:2] == "^^" ]

    # key lines start with an *
    # key lines have colon at least one char after the *
    # key lines have their first space after the colon
    key_lines = [ l for l in lines if 
                  ( l[:1] == "*" and 
                    l.find(":") >= 2 and
                    ( l.find(" ") > l.find(":") or l.find(" ") == -1 ) ) ]

    bad_lines = [ l for l in lines if l not in (ears_lines + key_lines) ]

    if bad_lines or not key_lines:
        rec_invalid_sec(sec, asset_id, "Invalid keyed information")
        problem = True

    # dictionary of keyed data
    keyed_data = {}
    for l in key_lines:
        k = l[1:l.find(":")].strip()
        v = l[l.find(":")+1:].strip()

        if k not in KEYS:
            rec_invalid_sec(sec, asset_id, "Invalid key")
            problem = True

        if v.find("*") != -1:
            rec_invalid_sec(sec, asset_id, "Value contains asterisk")
            problem = True

        # Keys are repeatable.  Accumulate a list of values.
        if k in keyed_data:
            keyed_data[k].append(v)
        else:
            keyed_data[k] = [v]
        

    r = {}
    r["problem"] = problem
    r["etd_type"] = "keyed"
    r["chyron_data"] = {}
    r["keyed_data"] = keyed_data
    r["catear_data"] = parse_catears(ears_lines, asset_id)
    return r



def parse_sec_chyron( sec: str, asset_id:str = None ) -> dict:
    """
    Parse as chyron data.
    (i.e., KSL Chyron note-4 conventions)
    """
    problem = False

    # get the non-empty lines
    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]

    ears_lines = [ l for l in lines if l[:2] == "^^" ]

    # KSL Note-4 style lines are the lines before the catear lines
    n4lines = [ l for l in lines if l not in ears_lines ]

    assert len(n4lines) >= 2, "Must have at least 2 note4-style lines for chyron sec"

    chyron_data = {}
    chyron_data["name_as_written"] = n4lines[0]
    chyron_data["name_normalized"] = n4lines[1]

    if len(n4lines) > 2:
        chyron_data["person_attributes"] = "; ".join(n4lines[2:])
    else:
        chyron_data["person_attributes"] = ""

    for k in ["name_as_written", "name_normalized", "person_attributes" ]:
        if chyron_data[k].find("^^") != -1:
            rec_invalid_sec(sec, asset_id, "Catears in chyron data")
            problem = True
    
    if len(chyron_data["name_normalized"]) > len(chyron_data["name_as_written"]) + 2:
        rec_invalid_sec(sec, asset_id, "Normalized name suspiciously long")
        problem = True

    r = {}
    r["problem"] = problem
    r["etd_type"] = "chyron"
    r["chyron_data"] = chyron_data
    r["keyed_data"] = {}
    r["catear_data"] = parse_catears(ears_lines, asset_id)
    return r



def parse_sec_ears_only( sec: str, asset_id:str = None ) -> dict:

    problem = False

    # get the non-empty lines
    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]

    ears_lines = [ l for l in lines if l[:2] == "^^" ]

    bad_lines = [ l for l in lines if l not in ears_lines ]

    if bad_lines:
        rec_invalid_sec(sec, asset_id, "Cat ears but then extra")
        problem = True


    r = {}
    r["problem"] = problem
    r["etd_type"] = "catears-only"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = parse_catears(ears_lines, asset_id)
    return r



def parse_sec_other( sec: str, asset_id:str = None ) -> dict:

    # this kind of etd is invalid.
    rec_invalid_sec(sec, asset_id, "Invalid section")
    problem = True

    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
    ears_lines = [ l for l in lines if l[:2] == "^^" ]

    r = {}
    r["problem"] = problem
    r["etd_type"] = "other"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = parse_catears(ears_lines, asset_id)
    return r



def parse_catears ( lines:list, asset_id:str = None ) -> dict:
    d = {}

    for l in lines:
        assert l[:2] == "^^", "Cat ear line must begin with '^^'"

        # TO DO: Analyze and fix this.
        # Should we allow more than one catear per line?
        # As of now, we do.  
        # As of now, we don't check that the catear name immediately follows ^^

        catears = [ c.strip() for c in l.split("^^") if c.strip() ]

        if len(catears) > 1:
            print(f"***  MORE THAN ONE CATEAR ON A LINE *** {asset_id}")
            print(l)
            #d["_problem"] = True
            pass

        for c in catears:
            invalid_catear = False

            # look for key-value catears
            if c.find(":") == 0:
                # Case: no earkey
                invalid_catear = True
            elif c.find(":") > 0:
                # Case: key-value-style earkey with colon
                # (Note that this would prevent using a colon in the value data)
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
                v = True
            
            if k not in CATEARS:
                invalid_catear = True
                rec_invalid_sec(l, asset_id, msg="Invalid catear")

            if not invalid_catear:
                d[k] = v
            else:
                d["_problem"] = True

    return d



def rec_invalid_sec( sec: str, asset_id:str = None, msg:str = None ):
    """
    Standard routine when encountering invalid etd data.

    For now, just prints out informative message.
    """

    print()
    if not msg:
        msg = "Invalid etd data"

    if asset_id:
        print(f"{msg} for {asset_id}:")
    else:
        print("Invalid etd data:")

    print("```")
    print(sec)
    print("```")
    print()

