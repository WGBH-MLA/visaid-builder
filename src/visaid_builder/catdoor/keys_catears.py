"""
keys_catears.py

Logic and vocabulary for specific catears and keys.

The logic here comes into play only after the "etd_text" has already
been parsed into keys (catear or normal) and their values.

Each of these functions returns a dictionary with two standard elements: 
"_problems" and "raw_value".  Additional elements are specific to the values
relevant to that particular catear or ETD key.


More key-specific and catear-specific fucntions may be added over time
to accomodate different types of data.
"""

import re


def nterm( v:str ) -> str:
    """
    Normalizes a term in a controlled list of terms.

    Takes a string representation of a term intended to be a controlled value 
    and normalizes it, making it suitable for lookups in lists of equivalently
    normalized representations of controlled terms.
    """
    # remove any non-alphanumerics
    v = "".join(c for c in v if c.isalnum())

    return v.lower()


############################################################################
# Key-specific parsing functions
# These are values in the dictionary below and need to be declared before
# that dictionary is created.
############################################################################

def parse_key_generic( v:str ) -> dict:
    """
    Generic key parser.
    Keys in the returned dict:
      - raw_value (str)
      - problems (list of str)
    """

    problems = []

    if v.find("*") != -1:
        problems.append("Warning: Key value contains asterisk.")

    d = {
        "raw_value": v,
        "_problems": problems
    }
    return d


def parse_key_genre( v:str ) -> dict:
    """
    Simple parser for 'genre' key.
    Keys in the returned dict:
      - raw_value (str)
      - problems (list of str)
      - genre (str) [Only if valid]
    """
    problems = []

    if nterm(v) in GENRES_d:
        genre = GENRES_d[nterm(v)]
    else:
        problems.append(f"Warning: Invalid genre '{v}'; will ignore.")
        genre = None

    d = {
        "raw_value": v,
        "_problems": problems,
    }
    if genre:
        d["genre"] = genre

    return d



def parse_key_topic( v:str ) -> dict:
    """
    Simple parser for 'topic' key.
    Keys in the returned dict:
      - raw_value (str)
      - problems (list of str)
      - topic (str)
    """    
    problems = []

    if nterm(v) in TOPICS_d:
        topic = TOPICS_d[nterm(v)]
    else:
        problems.append(f"Warning: Invalid topic '{v}'; will ignore.")
        topic = None

    d = {
        "raw_value": v,
        "_problems": problems,
    }
    if topic:
        d["topic"]= topic

    return d



def parse_key_contrib( v: str ) -> dict:
    """
    Custom parser for 'contrib' key.

    Parses values from lines like these:
        `*contrib: Manahan, Kent (Anchor) ^^home`
        `*contrib: Furber, Lincoln (Producer) ^^home ^^np`

    Keys in the returned dict:
      - raw_value (str)
      - problems (list of str)
      - name_normalized (str)
      - role (str)
      - home (bool) 
      - pictured (bool)
    """
    problems = []

    # Find the role in parenetheses
    rolematch = re.search(r'\((.*?)\)', v)

    if rolematch:
        # name is everything up to parenthesis
        name = v.split("(")[0].strip()

        # role is what is in parentheses
        role_str = rolematch.group(1).strip()
        if nterm(role_str) in ROLES_d:
            role = ROLES_d[nterm(role_str)]
        else:
            problems.append(f"Invalid role '{v}'; will ignore.")
            role = None
    else:
        name = v.split("^")[0].strip()
        role = None        

    # Find all inline catear tags (capturing the alphanumeric characters directly following '^^')
    inline_tags = re.findall(r'\^\^(\w*)', v)

    # Set boolean flags based on presence of the valid tags
    home = "home" in inline_tags
    pictured = "np" not in inline_tags
    
    # Validate that every inline catear matches our allowed tags list
    for tag in inline_tags:
        if tag not in ["home", "np"]:
            problems.append(f"Invalid in-line cat ear '^^{tag}' for `*contrib`; will ignore.")

    d = {
        "raw_value": v,
        "_problems": problems,
        "name_normalized": name,
        "role": role,
        "home": home,
        "pictured": pictured
    }
    return d



############################################################################
# Catear-specific parsing functions
############################################################################

def parse_catear_generic( v:str ) -> dict:
    problems = []
    alerts = []

    if v.find("^") != -1:
        problems.append("Warning: Cat ear value contains caret.")

    d = {
        "raw_value": v,
        "_problems": problems,
        "_alerts": alerts,
    }
    return d


def parse_catear_role( v:str ) -> dict:
    problems = []
    alerts = []    

    if nterm(v) in ROLES_d:
        role = ROLES_d[nterm(v)]
    else:
        problems.append("Invalid role")
        role = None

    d = {
        "raw_value": v,
        "_problems": problems,
        "_alerts": alerts,
    }
    if role:
        d["role"] = role

    return d


def parse_catear_sens( v:str ) -> dict:
    problems = []
    alerts = []    

    if v.find("^") != -1:
        problems.append("Warning: Cat ear value contains caret.")

    alerts.append("Alert: Content review needed.")

    d = {
        "raw_value": v,
        "_problems": problems,
        "_alerts": alerts,        
    }
    return d



############################################################################
# Vocabularies 
#
# expressed as dispatch tables or lists
############################################################################

CHYRON_SEC_CATEARS = {
    "home":            parse_catear_generic,
    "np":              parse_catear_generic,
    "role":            parse_catear_role,
    "omit-attributes": parse_catear_sens,
}
GENERAL_CATEARS =  {
    "miss":            parse_catear_generic,
    "sens":            parse_catear_sens,
    "cw":              parse_catear_sens,
    "note":            parse_catear_sens,
    "social":          parse_catear_generic,
}
CATEARS = CHYRON_SEC_CATEARS | GENERAL_CATEARS

KEYS = {
    "contrib":         parse_key_contrib,
    "prod":            parse_key_generic,
    "dir":             parse_key_generic,
    "cam":             parse_key_generic,
    "air":             parse_key_generic,
    "rec":             parse_key_generic,
    "date":            parse_key_generic,
    "copyright-year":  parse_key_generic,
    "copyright-owner": parse_key_generic,
    "copr":            parse_key_generic, 
    "prog-title":      parse_key_generic,
    "series-title":    parse_key_generic,
    "ep-title":        parse_key_generic, 
    "ep-no":           parse_key_generic,
    "title":           parse_key_generic,
    "prog-desc":       parse_key_generic,
    "ep-desc":         parse_key_generic, 
    "genre":           parse_key_genre,
    "topic":           parse_key_topic,
    "geo":             parse_key_generic,
    "bumper":          parse_key_generic,
    "performance":     parse_key_generic,
}

# from local controlled vocabulary
# https://github.com/WGBH-MLA/ams/blob/develop/config/authorities/contributor_role.yml
# (Should be updated to reflect any additions or changes to the above.)
ROLES = [
    "Actor",
    "Adapter",
    "Appearing",
    "Anchor",
    "Artist",
    "Artistic Director",
    "Artistic Supervisor",
    "Assistant Director",
    "Assistant Producer",
    "Associate Director",
    "Associate Producer",
    "Author",
    "Broadcast Engineer",
    "Camera Operator",
    "Caption Writer",
    "Casting Director",
    "Choreographer",
    "Cinematographer",
    "Co-Producer",
    "Commentator",
    "Composer",
    "Concept",
    "Concept Artist",
    "Conductor",
    "Content Supervision",
    "Coordinating Director",
    "Coordinating Producer",
    "Copyright Holder",
    "Costume Designer",
    "Crew",
    "Describer",
    "Director",
    "Director of Photographer",
    "Distributor",
    "Editor",
    "Engineer",
    "Executive Director",
    "Executive Producer",
    "Filmmaker",
    "Foley Artist",
    "Graphic Designer",
    "Graphic Editor",
    "Guest",
    "Host",
    "Illustrator",
    "Interviewee",
    "Interviewer",
    "Lighting Technician",
    "Make-Up Artist",
    "Moderator",
    "Music Supervisor",
    "Musician",
    "Narrator",
    "Panelist",
    "Performer",
    "Performing Group",
    "Photographer",
    "Presenter",
    "Producer",
    "Production Manager",
    "Production Unit",
    "Program Associate",
    "Project Coordinator",
    "Project Director",
    "Project Supervisor",
    "Publisher",
    "Recoding Engineer",
    "Reporter",
    "Screenwriter",
    "Set Designer",
    "Sound Designer",
    "Sound Editor",
    "Speaker",
    "Sponsor",
    "Story Supervisor",
    "Supervisory Producer",
    "Technical Director",
    "Video Engineer",
    "Vocalist",
    "Voiceover Artist",
    "Writer",
]
# create a dictionary for lower-case validation
ROLES_d = { nterm(k): k for k in set(ROLES) }


# from local controlled vocabulary
# https://github.com/WGBH-MLA/ams/blob/develop/config/authorities/topics.yml
# (Should be updated to reflect any additions or changes to the above.)
TOPICS = [
    "Agriculture",
    "Animals",
    "Antiques and Collectibles",
    "Architecture",
    "Biography",
    "Business",
    "Consumer Affairs and Advocacy",
    "Crafts",
    "Dance",
    "Economics",
    "Education",
    "Employment",
    "Exercise",
    "Fine Arts",
    "Film and Television",
    "Food and Cooking",
    "Gardening",
    "Geography",
    "Global Affairs",
    "Health",
    "History",
    "Holiday",
    "Home Improvement",
    "Humor",
    "Journalism",
    "Law Enforcement and Crime",
    "LGBTQ",
    "Literature",
    "Local Communities",
    "Medicine",
    "Military Forces and Armaments",
    "Music",
    "Nature",
    "News",
    "Parenting",
    "Performing Arts",
    "Philosophy",
    "Politics and Government",
    "Psychology",
    "Public Affairs",
    "Race and Ethnicity",
    "Religion",
    "Science",
    "Social Issues",
    "Spanish Language",
    "Sports",
    "Technology",
    "Theater",
    "Transportation",
    "Travel",
    "War and Conflict",
    "Weather",
    "Women",
]
# create a dictionary for lower-case validation
TOPICS_d = { nterm(k): k for k in set(TOPICS) }


# from local controlled vocabulary
# https://github.com/WGBH-MLA/ams/blob/develop/config/authorities/genre.yml
# (Should be updated to reflect any additions or changes to the above.)
GENRES  = [
    "Call-in",
    "Children's",
    "Debate",
    "Documentary",
    "Drama",
    "Educational",
    "Event Coverage",
    "Fundraiser",
    "Game Show",
    "Instructional",
    "Interview",
    "Magazine",
    "News Report",
    "Performance",
    "Promo",
    "Public Service Announcement",
    "Recorded Music",
    "Special",
    "Talk Show",
]
# create a dictionary for lower-case validation
GENRES_d = { nterm(k): k for k in set(GENRES) }
