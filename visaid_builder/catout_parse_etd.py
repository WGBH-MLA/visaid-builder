"""
catout_parse_etd.py

Parsing logic for the editor text document (etd) field that is part of a
catout entry.

The logic here assumes specific rules and conventions for structuring
the data in the editor fields of cataids.

"""

# not used yet
VALID_CATEARS = [
    "home",
    "away",
    "miss",
    "sens",
    "cw",
    "note",
    "np" ]



def parse_etd( etd_text:str ) -> list:
    """
    Parsing logic of human edited/entered values.
    Takes a string of raw text as input.
    Returns a list of dictionaries.

    Typically, the returned list has just a single dictionary, but if the 
    user has used the "+++" syntax to multiplex the editor, there may be more
    than one.

    This function divides muliplexed editor text, uses a heuristic to choose
    the appropriate parsing, and then calls the appropriate parsing function.
    """

    # allow multiple records per etd text
    etd_recs = []

    # divide multiplexed editor text and strip surrounding whitespace
    etd_secs = [ s.strip() for s in etd_text.split("\n+++") if s.strip() ]

    for sec in etd_secs:

        lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
        ears_lines = [ l for l in lines if l[:2] == "^^" ]

        if not len(sec):
            # empty section
            r = parse_sec_empty(sec)
        elif sec[0] == "*":
            # starts with asterisk -> keyed data section
            r = parse_sec_keyed(sec)
        elif ( len(lines) - len(ears_lines) )  >= 2:
            # at least two non-catears lines -> chyron data section
            r = parse_sec_chyron(sec)
        else:
            # other etd value
            r = parse_sec_other(sec)

        etd_recs.append(r)

    return etd_recs



def parse_sec_empty( sec:str ) -> dict:
    r = {}
    r["etd_type"] = "empty"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = {}
    return r



def parse_sec_keyed( sec:str ) -> dict:
    """
    Parse as keyed/bullet list of values
    """

    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
    ears_lines = [ l for l in lines if l[:2] == "^^" ]
    key_lines = [ l for l in lines if 
                  ( l[:1] == "*" and 
                    l.find(":") >= 2 and
                    ( l.find(" ") > l.find(":") or l.find(" ") == -1 ) ) ]

    d = {}
    for l in key_lines:
        k = l[1:l.find(":")]
        v = l[l.find(":")+1:].strip()
        d.setdefault(k, []).append(v)

    r = {}
    r["etd_type"] = "keyed"
    r["chyron_data"] = {}
    r["keyed_data"] = d
    r["catear_data"] = parse_catears(ears_lines)
    return r



def parse_sec_chyron( sec:str ) -> dict:
    """
    Parse as chyron data
    (i.e., KSL Chyron note-4 conventions)
    """

    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
    ears_lines = [ l for l in lines if l[:2] == "^^" ]
    n4lines = [ l for l in lines if l not in ears_lines ]

    assert len(n4lines) >= 2, "Must have at least 2 note4-style lines for chyron sec"

    d = {}
    d["name_as_written"] = n4lines[0]
    d["name_normalized"] = n4lines[1]

    if len(n4lines) > 2:
        d["person_attributes"] = "; ".join(n4lines[2:])
    else:
        d["person_attributes"] = ""

    r = {}
    r["etd_type"] = "chyron"
    r["chyron_data"] = d
    r["keyed_data"] = {}
    r["catear_data"] = parse_catears(ears_lines)
    return r



def parse_sec_other( sec:str ) -> dict:

    lines = [ s.strip() for s in sec.split("\n") if s.strip() ]
    ears_lines = [ l for l in lines if l[:2] == "^^" ]

    r = {}
    r["etd_type"] = "other"
    r["chyron_data"] = {}
    r["keyed_data"] = {}
    r["catear_data"] = parse_catears(ears_lines)
    return r



def parse_catears ( lines:list ) -> dict:
    d = {}

    for l in lines:
        assert l[:2] == "^^", "Cat ear line must begin with '^^'"

        # potentially allow more than one catear per line
        catears = [ c.strip() for c in l.split("^^") if c.strip() ]

        for c in catears:
            invalid_catear = False

            # look for key-value catears
            if c.find(":") == 0:
                invalid_catear = True

            elif c.find(":") > 0:
                # key is substring up to colon
                k = c[:c.find(":")]
                # value is everything after
                v = c[c.find(":")+1:].strip()
            
            elif c.find(" ") != -1:
                # key is substring up to first space
                k = c[:c.find(" ")]
                # value is everything after
                v = c[c.find(" ")+1:].strip()

            else:
                # non-key-value catear
                k = c
                v = True
            
            if not k.isalnum():
                invalid_catear = True

            if not invalid_catear:
                d[k] = v

    return d
