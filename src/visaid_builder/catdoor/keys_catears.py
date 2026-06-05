"""
keys_catears.py

Vocabulary and logic for specific catears and keys.

The logic here comes into play only after the "etd_text" has already
been parsed into keys (catear or normal) and their values.

More key-specific and catear-specific fucntions may be added over time
to accomodate different types of data.
"""

import re

############################################################################
# Key-specific parsing functions
############################################################################

def parse_key_contrib( v: str ) -> dict:
    problems = []

    # Find the role in parenetheses
    rolematch = re.search(r'\((.*?)\)', v)

    if rolematch:
        # name is everything up to parenthesis
        name = v.split("(")[0].strip()

        # role is what is in parentheses
        role_str = rolematch.group(1).strip()
        if role_str in ROLES:
            role = role_str
        else:
            problems.append("Invalid role")
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
            problems.append("Invalid catear")
            break

    d = {
        "raw_value": v,
        "problems": problems,
        "name_normalized": name,
        "role": role,
        "home": home,
        "pictured": pictured
    }
    return d


def parse_key_generic( v:str ) -> dict:
    problems = []

    if v.find("*") != -1:
        problems.append("Key value contains asterisk")

    d = {
        "raw_value": v,
        "problems": problems
    }
    return d


############################################################################
# Catear-specific parsing functions
############################################################################

def parse_catear_role( v:str ) -> dict:
    problems = []

    if v.strip() in ROLES:
        role = v.strip()
    else:
        problems.append("Invalid role")
        role = None

    d = {
        "raw_value": v,
        "problems": problems,
        "role": role
    }
    return d


def parse_catear_generic( v:str ) -> dict:
    problems = []

    if v.find("^") != -1:
        problems.append("Catear value contains caret")

    d = {
        "raw_value": v,
        "problems": problems
    }
    return d



############################################################################
# Vocabularies 
#
# expressed as dispatch tables or lists
############################################################################

CATEARS = {
    "home": parse_catear_generic,
    "miss": parse_catear_generic,
    "sens": parse_catear_generic,
    "cw":   parse_catear_generic,
    "note": parse_catear_generic,
    "np":   parse_catear_generic,
    "role": parse_catear_role
}


KEYS = {
    "contrib": parse_key_contrib,
    "air": parse_key_generic,
    "rec": parse_key_generic,
    "copyright-year": parse_key_generic,
    "copyright-owner": parse_key_generic,
    "copr": parse_key_generic, 
    "date": parse_key_generic,
    "prog-title": parse_key_generic,
    "series-title": parse_key_generic,
    "ep-title": parse_key_generic, 
    "title": parse_key_generic,
    "ep-no": parse_key_generic,
    "dir": parse_key_generic,
    "prod": parse_key_generic,
    "cam": parse_key_generic
}

# from locoal controlled vocabulary
# https://github.com/WGBH-MLA/ams/blob/develop/config/authorities/contributor_role.yml
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
    "Writer"
]

