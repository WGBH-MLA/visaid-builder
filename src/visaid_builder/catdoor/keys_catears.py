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

def parse_key_generic( v:str ) -> dict:
    problems = []

    if v.find("*") != -1:
        problems.append("Key value contains asterisk")

    d = {
        "raw_value": v,
        "problems": problems
    }
    return d


def parse_key_genre( v:str ) -> dict:
    problems = []

    genre_str = v.strip()
    if topic_str in GENRES:
        genre = genres_str
    else:
        problems.append("Invalid genre")
        genre = None

    d = {
        "raw_value": v,
        "problems": problems,
        "genre": genre
    }
    return d



def parse_key_topic( v:str ) -> dict:
    problems = []

    topic_str = v.strip()
    if topic_str in TOPICS:
        topic = topics_str
    else:
        problems.append("Invalid topic")
        topic = None

    d = {
        "raw_value": v,
        "problems": problems,
        "topic": topic
    }
    return d



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



############################################################################
# Catear-specific parsing functions
############################################################################

def parse_catear_generic( v:str ) -> dict:
    problems = []

    if v.find("^") != -1:
        problems.append("Catear value contains caret")

    d = {
        "raw_value": v,
        "problems": problems
    }
    return d


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



############################################################################
# Vocabularies 
#
# expressed as dispatch tables or lists
############################################################################

CATEARS = {
    "home":   parse_catear_generic,
    "miss":   parse_catear_generic,
    "sens":   parse_catear_generic,
    "cw":     parse_catear_generic,
    "note":   parse_catear_generic,
    "social": parse_catear_generic,
    "np":     parse_catear_generic,
    "role":   parse_catear_role
}


KEYS = {
    "contrib": parse_key_contrib,
    "air": parse_key_generic,
    "rec": parse_key_generic,
    "copyright-year": parse_key_generic,
    "copyright-owner": parse_key_generic,
    "copr": parse_key_generic, 
    "date": parse_key_generic,
    "genre": parse_key_generic,
    "geo": parse_key_generic,
    "topic": parse_key_generic,
    "prog-title": parse_key_generic,
    "series-title": parse_key_generic,
    "ep-title": parse_key_generic, 
    "title": parse_key_generic,
    "ep-no": parse_key_generic,
    "dir": parse_key_generic,
    "prod": parse_key_generic,
    "cam": parse_key_generic
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
    "Writer"
]

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
    "Women"    
]

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
    "Talk Show"
]