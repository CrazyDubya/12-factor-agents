"""
Complete Staten Island/Richmond County official profiles database.
Contains all 11 current officials across federal, state, and municipal levels.
"""
from datetime import datetime
from typing import Dict, List, Optional
from models.official import Official, Position, PositionType

# Complete Staten Island Official Profiles Database
STATEN_ISLAND_OFFICIALS = {
    "federal": {
        "schumer_chuck": {
            "bioguide_id": "S000148",
            "full_name": "Charles Ellis Schumer",
            "first_name": "Charles",
            "last_name": "Schumer",
            "nickname": "Chuck",
            "party": "Democratic",
            "date_of_birth": datetime(1950, 11, 23),
            "state": "New York",
            "jurisdiction_level": "federal",
            "currently_serving": True,
            "website": "https://www.schumer.senate.gov",
            "twitter_handle": "@SenSchumer",
            "facebook_url": "https://facebook.com/senschumer",
            "email": "Available through website contact form",
            "phone": "(202) 224-6542",
            "positions": [{
                "position_type": PositionType.SENATOR,
                "title": "U.S. Senator from New York",
                "chamber": "Senate",
                "start_date": datetime(1999, 1, 6),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["Senate Majority Leader (2021-2025)", "Senate Democratic Leader (2017-present)"],
                "committees": ["Ex Officio status on all committees as Democratic Leader"]
            }],
            "career_highlights": [
                "First Jewish Senate Majority Leader in U.S. history",
                "First New Yorker to serve as Senate Majority Leader",
                "Longest-serving Senator from New York",
                "Previous: U.S. House of Representatives (1981-1999)"
            ],
            "staten_island_focus": {
                "major_investments": [
                    {"project": "Living Breakwaters", "amount": 107000000, "year": 2024},
                    {"project": "Staten Island Ferry upgrades", "amount": 190000000, "year": 2021},
                    {"project": "Army Corps coastal protection", "amount": 2000000000, "year": "2013-2025"},
                    {"project": "Bluebelt expansion Midland Beach", "amount": 40500000, "year": 2013}
                ],
                "key_initiatives": [
                    "Post-Hurricane Sandy infrastructure recovery",
                    "MTA accessibility improvements for Staten Island Railway",
                    "Federal transportation funding advocacy",
                    "Coastal protection and resilience projects"
                ]
            }
        },
        "gillibrand_kirsten": {
            "bioguide_id": "G000555",
            "full_name": "Kirsten Elizabeth Gillibrand",
            "first_name": "Kirsten",
            "last_name": "Gillibrand",
            "party": "Democratic",
            "date_of_birth": datetime(1966, 12, 9),
            "state": "New York",
            "jurisdiction_level": "federal",
            "currently_serving": True,
            "website": "https://www.gillibrand.senate.gov",
            "twitter_handle": "@SenGillibrand",
            "positions": [{
                "position_type": PositionType.SENATOR,
                "title": "U.S. Senator from New York",
                "chamber": "Senate",
                "start_date": datetime(2009, 1, 27),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["DSCC Chair (2025-2027)"],
                "committees": ["Armed Services", "Appropriations", "Intelligence", "Special Committee on Aging"]
            }],
            "ideological_evolution": {
                "house_period": "Conservative Blue Dog Democrat (2007-2009)",
                "early_senate": "Progressive transformation (2009-2020)",
                "current_period": "Pragmatic centrist as DSCC Chair (2025-present)"
            },
            "staten_island_focus": {
                "direct_investments": [
                    {"project": "Community Health Center of Richmond", "amount": 487500, "year": 2010},
                    {"project": "Staten Island Ferry upgrades", "amount": 6000000, "year": 2015},
                    {"project": "Staten Island Museum grant", "amount": 12000, "year": 2018}
                ],
                "key_initiatives": [
                    "9/11 First Responders healthcare (James Zadroga Act)",
                    "Head Start grants for Brooklyn & Staten Island",
                    "Port Richmond Avenue health center expansion"
                ]
            }
        },
        "malliotakis_nicole": {
            "bioguide_id": "M001204",
            "full_name": "Nicole R. Malliotakis",
            "first_name": "Nicole",
            "last_name": "Malliotakis",
            "party": "Republican",
            "date_of_birth": datetime(1980, 11, 11),
            "state": "New York",
            "congressional_district": "11",
            "county": "Richmond County",
            "borough": "Staten Island",
            "jurisdiction_level": "federal",
            "currently_serving": True,
            "website": "https://malliotakis.house.gov",
            "twitter_handle": "@RepMalliotakis",
            "positions": [{
                "position_type": PositionType.REPRESENTATIVE,
                "title": "U.S. Representative for New York's 11th Congressional District",
                "chamber": "House",
                "start_date": datetime(2021, 1, 3),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["Assistant Whip, House Republican Conference"],
                "committees": ["Ways and Means Committee", "Joint Economic Committee"]
            }],
            "background": {
                "heritage": "First-generation American (Greek father, Cuban mother)",
                "previous_positions": [
                    "NYC Mayoral candidate (2017)",
                    "NY State Assembly 60th/64th District (2010-2020)",
                    "Assembly Minority Whip"
                ]
            },
            "staten_island_focus": {
                "federal_funding_secured": 230000000,
                "infrastructure_investments": [
                    {"project": "St. George Ferry Terminal upgrades", "amount": 5750000, "year": 2024},
                    {"project": "Mid-Island Bluebelt reconstruction", "amount": 1000000, "year": 2023},
                    {"project": "Staten Island Expressway bridge work", "amount": "TBD", "year": 2024}
                ],
                "legislative_priorities": [
                    "Opposition to Manhattan congestion pricing",
                    "SALT deduction increases (quadrupling to $40,000)",
                    "Enhanced ferry service advocacy",
                    "Immigration enforcement and border security"
                ]
            }
        }
    },
    "state": {
        "lanza_andrew": {
            "full_name": "Andrew Joseph Lanza",
            "first_name": "Andrew",
            "last_name": "Lanza",
            "party": "Republican",
            "date_of_birth": datetime(1964, 3, 12),
            "state": "New York",
            "state_senate_district": "24",
            "county": "Richmond County",
            "borough": "Staten Island",
            "jurisdiction_level": "state",
            "currently_serving": True,
            "website": "https://nysenate.gov/senators/andrew-j-lanza",
            "phone": "(718) 984-4073",
            "positions": [{
                "position_type": PositionType.STATE_SENATOR,
                "title": "New York State Senator, 24th District",
                "chamber": "Senate",
                "start_date": datetime(2007, 1, 1),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["Deputy Minority Leader", "Floor Leader"],
                "committees": ["Finance Committee", "Former Codes Committee Chairman"]
            }],
            "unique_status": "Only state senator representing district wholly contained within Staten Island",
            "background": {
                "education": ["Monsignor Farrell High School", "St. John's University (B.S. Accounting)", "Fordham Law School (J.D.)"],
                "professional": ["Former Assistant District Attorney", "KPMG Senior Auditor", "Private practice attorney"],
                "family": "Wife Marcele (NYC teacher), three children",
                "residence": "Great Kills, Staten Island"
            },
            "staten_island_focus": {
                "major_achievements": [
                    {"project": "13th Judicial District creation", "description": "Historic legislation creating Staten Island's own judicial district", "year": 2020},
                    {"project": "Living Breakwaters", "amount": 107000000, "description": "7-year collaboration with Senator Schumer", "year": "2017-2024"},
                    {"project": "Arthur Kill Railway Station", "description": "First new SI railway station in 20+ years", "year": 2023},
                    {"project": "MTA Board representation requirement", "description": "Legislation requiring Staten Island representation", "year": 2022}
                ],
                "legislative_priorities": [
                    "Flood protection and coastal resilience",
                    "MTA reform and accountability",
                    "Anti-overdevelopment zoning laws",
                    "Property tax cap for middle-class relief",
                    "Enhanced penalties for MTA crimes"
                ]
            }
        },
        "fall_charles": {
            "full_name": "Charles D. Fall",
            "first_name": "Charles",
            "last_name": "Fall",
            "party": "Democratic",
            "state": "New York",
            "state_assembly_district": "61",
            "county": "Richmond County",
            "borough": "Staten Island",
            "jurisdiction_level": "state",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.STATE_ASSEMBLY,
                "title": "New York State Assemblymember, 61st District",
                "chamber": "Assembly",
                "start_date": datetime(2019, 1, 1),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["Deputy Majority Leader (2025)", "Assistant Majority Leader"],
                "committees": ["Consumer Fraud Protection Subcommittee Chair"]
            }],
            "historic_significance": "First Muslim and African American Assemblymember elected from Staten Island",
            "background": {
                "succession": "Replaced Matthew Titone (2007-2019)",
                "district_coverage": "North Shore Staten Island, Lower Manhattan, Parts of Brooklyn"
            }
        },
        "reilly_michael": {
            "full_name": "Michael Reilly",
            "first_name": "Michael",
            "last_name": "Reilly",
            "party": "Republican",
            "state": "New York",
            "state_assembly_district": "62",
            "county": "Richmond County",
            "borough": "Staten Island",
            "jurisdiction_level": "state",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.STATE_ASSEMBLY,
                "title": "New York State Assemblymember, 62nd District",
                "chamber": "Assembly",
                "start_date": datetime(2018, 1, 1),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["Ranking Minority Member of Standing Committee on Cities"],
                "committees": ["Cities", "Alcoholism and Drug Abuse", "Aging", "Housing", "Higher Education"]
            }],
            "background": {
                "district_coverage": "South Shore Staten Island",
                "legislative_focus": "Infrastructure, transportation safety, municipal governance"
            }
        },
        "pirozzolo_sam": {
            "full_name": "Sam Pirozzolo",
            "first_name": "Sam",
            "last_name": "Pirozzolo",
            "party": "Republican",
            "state": "New York",
            "state_assembly_district": "63",
            "county": "Richmond County",
            "borough": "Staten Island",
            "jurisdiction_level": "state",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.STATE_ASSEMBLY,
                "title": "New York State Assemblymember, 63rd District",
                "chamber": "Assembly",
                "start_date": datetime(2023, 1, 1),
                "end_date": None,
                "is_current": True,
                "committees": ["Joint Budget Conference Committee on Economic Development"]
            }],
            "electoral_significance": {
                "party_flip": "First Republican to win this seat since 1982",
                "defeated_incumbent": "Michael Cusick (D, 2003-2023) - 20-year veteran"
            },
            "background": {
                "profession": "Family optical practice owner (33 years)",
                "community_service": "Former president of Community Education Council 31",
                "district_coverage": "Western/Central Staten Island"
            }
        },
        "tannousis_michael": {
            "full_name": "Michael Tannousis",
            "first_name": "Michael",
            "last_name": "Tannousis",
            "party": "Republican",
            "state": "New York",
            "state_assembly_district": "64",
            "county": "Richmond County",
            "borough": "Staten Island",
            "jurisdiction_level": "state",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.STATE_ASSEMBLY,
                "title": "New York State Assemblymember, 64th District",
                "chamber": "Assembly",
                "start_date": datetime(2021, 1, 1),
                "end_date": None,
                "is_current": True
            }],
            "background": {
                "succession": "Replaced Nicole Malliotakis when she moved to Congress (2021)",
                "profession": "Attorney and former prosecutor",
                "district_coverage": "East Shore Staten Island, Bay Ridge Brooklyn"
            }
        }
    },
    "municipal": {
        "hanks_kamillah": {
            "full_name": "Kamillah Hanks",
            "first_name": "Kamillah",
            "last_name": "Hanks",
            "party": "Democratic",
            "state": "New York",
            "city": "New York City",
            "borough": "Staten Island",
            "council_district": "49",
            "jurisdiction_level": "municipal",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.CITY_COUNCIL,
                "title": "NYC Council Member, District 49",
                "start_date": datetime(2022, 1, 1),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["Chair of Subcommittee on Landmarks, Public Sitings and Dispositions"],
                "committees": ["Finance", "Land Use", "Civil Service and Labor", "Cultural Affairs", "Education"]
            }],
            "background": {
                "tenure": "First term (2022-present), reelected in June 2025 primary with ~60%",
                "district_coverage": "North Shore Staten Island",
                "focus": "Smart growth and economic development",
                "personal": "Lifelong Staten Islander, mother of four, 20 years community development"
            }
        },
        "carr_david": {
            "full_name": "David Carr",
            "first_name": "David",
            "last_name": "Carr",
            "party": "Republican",
            "state": "New York",
            "city": "New York City",
            "borough": "Staten Island",
            "council_district": "50",
            "jurisdiction_level": "municipal",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.CITY_COUNCIL,
                "title": "NYC Council Member, District 50",
                "start_date": datetime(2021, 1, 1),
                "end_date": None,
                "is_current": True,
                "leadership_roles": ["NYC Council Minority Leader (2025)"],
                "committees": ["Finance", "Parks and Recreation", "Sanitation", "Cultural Affairs", "Governmental Operations", "Standards and Ethics"]
            }],
            "background": {
                "historic_significance": "First openly gay Republican on City Council, only openly gay elected representative for Staten Island",
                "district_changes": "District 50 became two-borough (Staten Island + Brooklyn) after 2023 redistricting",
                "previous_role": "Chief of Staff to predecessor Joe Matteo for eight years"
            }
        },
        "morano_frank": {
            "full_name": "Frank Morano",
            "first_name": "Frank",
            "last_name": "Morano",
            "party": "Republican",
            "state": "New York",
            "city": "New York City",
            "borough": "Staten Island",
            "council_district": "51",
            "jurisdiction_level": "municipal",
            "currently_serving": True,
            "positions": [{
                "position_type": PositionType.CITY_COUNCIL,
                "title": "NYC Council Member, District 51",
                "start_date": datetime(2025, 5, 1),
                "end_date": None,
                "is_current": True
            }],
            "background": {
                "recent_election": "Won April 29, 2025 special election with 59% of vote",
                "profession": "Radio host on 77WABC",
                "previous_role": "Part-time staffer in Joe Borelli's office",
                "succession": "Replaced Joe Borelli (resigned January 31, 2025 for private sector)"
            }
        }
    }
}

# Historical Electoral Changes (2000-2025)
ELECTORAL_TRANSITIONS = {
    "major_shifts": [
        {
            "year": 2007,
            "change": "Andrew Lanza moves from NYC Council to State Senate",
            "replaced": "John J. Marchi (50-year veteran)",
            "significance": "Generational change in State Senate representation"
        },
        {
            "year": 2018,
            "change": "NY Senate flips Democratic control",
            "impact": "Lanza becomes lone Republican representing NYC in State Senate"
        },
        {
            "year": 2020,
            "change": "Nicole Malliotakis elected to Congress",
            "significance": "Staten Island gets dedicated Republican federal representative"
        },
        {
            "year": 2023,
            "change": "Assembly District 63 flips Republican",
            "details": "Sam Pirozzolo defeats Michael Cusick (20-year Democratic incumbent)",
            "significance": "First Republican in seat since 1982"
        },
        {
            "year": 2025,
            "change": "Council District 50 becomes two-borough",
            "details": "Redistricting adds Brooklyn neighborhoods to Staten Island district"
        }
    ],
    "party_control_evolution": {
        "2000": "Mixed representation across levels",
        "2007": "Republican strength in State Senate/Assembly",
        "2018": "Democratic state control, Republican federal/local strength",
        "2023": "Increasing Republican Assembly representation",
        "2025": "Balanced federal (mixed), strong Republican state/local representation"
    }
}

# Cross-Jurisdictional Relationships
DOCUMENTED_RELATIONSHIPS = {
    "schumer_lanza": {
        "type": "Direct Cooperation",
        "evidence_level": "High",
        "key_projects": [
            {
                "name": "Living Breakwaters",
                "duration": "2017-2024",
                "evidence": "Lanza quote: '7 years of working jointly with Senator Schumer'",
                "outcome": "$107 million coastal resiliency project"
            },
            {
                "name": "Staten Island Seawall",
                "year": 2016,
                "evidence": "Joint press conference with shared statements",
                "outcome": "Army Corps approval ahead of schedule"
            }
        ],
        "evolution": "Crisis-driven cooperation post-Hurricane Sandy (2012) transformed into sustained partnership"
    },
    "republican_coalition": {
        "type": "Strategic Alignment",
        "evidence_level": "Moderate",
        "members": ["Malliotakis", "Lanza", "Reilly", "Pirozzolo", "Tannousis", "Carr", "Morano"],
        "coordination_areas": [
            "Opposition to congestion pricing",
            "Property tax relief advocacy",
            "MTA reform and accountability",
            "Anti-overdevelopment initiatives"
        ]
    },
    "assembly_coordination": {
        "type": "Legislative Coordination",
        "evidence_level": "Moderate",
        "examples": [
            {
                "initiative": "Battery Energy Storage Opposition",
                "participants": ["Lanza", "Pirozzolo", "Reilly"],
                "evidence": "Joint letters to PSC, coordinated legislation"
            },
            {
                "initiative": "Infrastructure funding",
                "participants": ["Lanza", "Fall"],
                "evidence": "$46 million bridge rehabilitation joint effort (2022)"
            }
        ]
    }
}