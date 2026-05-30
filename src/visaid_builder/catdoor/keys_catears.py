"""
keys_catears.py

Vocabulary and logic for specific catears and keys.

The logic here comes into play only after the "etd_text" has already
been parsed into keys (catear or normal) and their values.
"""

import re

############################################################################
# Key-specific parsing functions
############################################################################

def parse_key_contrib( v: str ) -> dict:
    problem = False

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
            problem = True
            role = None
    else:
        name = v.split("^")[0].strip()
        role = None        

    # Check for a ^^home catear flag
    if v.find("^^home") != -1:
        home = True
    else:
        home = False

    # Check for the ^^np 
    if v.find("^^np") != -1:
        pictured = False
    else:
        pictured = True

    d = {
        "problem": problem,
        "name_normalized": name,
        "role": role,
        "home": home,
        "pictured": pictured
    }
    return d


def parse_catear_role( v:str ) -> dict:
    problem = False

    if v.strip() in ROLES:
        role = v.strip()
    else:
        problem = True
        role = None

    d = {
        "problem": problem,
        "role": role
    }
    return d



############################################################################
# Vocabularies 
#
# expressed as dispatch tables or lists
############################################################################

CATEARS = {
    "home": None,
    "miss": None,
    "sens": None,
    "cw":   None,
    "note": None,
    "np":   None,
    "role": parse_catear_role
}


KEYS = {
    "contrib": parse_key_contrib,
    "air": None,
    "rec": None,
    "copyright-year": None,
    "copyright-owner": None,
    "copr": None, 
    "date": None,
    "prog-title": None,
    "series-title": None,
    "ep-title": None, 
    "title": None,
    "ep-no": None,
    "dir": None,
    "prod": None,
    "cam": None
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

