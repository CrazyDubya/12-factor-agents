"""
Comprehensive predecessor mapping for Staten Island officials (2000-2025).
Maps all officials who held key positions representing Staten Island over 25 years.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class OfficialTenure:
    """Represents an official's tenure in a specific position."""
    name: str
    position: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    party: str
    election_years: List[int]
    key_achievements: List[str]
    transition_reason: str  # "defeated", "retired", "moved_to_other_office", "resigned"
    predecessor: Optional[str] = None
    successor: Optional[str] = None


# Comprehensive predecessor mapping for Staten Island representation (2000-2025)
STATEN_ISLAND_PREDECESSORS = {

    # ==================== FEDERAL LEVEL ====================

    "us_senate_ny_senior": [
        OfficialTenure(
            name="Daniel Patrick Moynihan",
            position="US Senator (NY Senior)",
            start_date="1977-01-03",  # Started before our period
            end_date="2001-01-03",
            party="Democratic",
            election_years=[1976, 1982, 1988, 1994],
            key_achievements=[
                "Chair of Senate Finance Committee",
                "Social Security reform leadership",
                "Infrastructure advocacy",
                "Urban policy expertise"
            ],
            transition_reason="retired",
            successor="Charles Schumer"
        ),
        OfficialTenure(
            name="Charles Schumer",
            position="US Senator (NY Senior)",
            start_date="2001-01-03",
            end_date="2025-01-03",  # Current
            party="Democratic",
            election_years=[1998, 2004, 2010, 2016, 2022],
            key_achievements=[
                "Senate Majority Leader (2021-present)",
                "Senate Minority Leader (2017-2021)",
                "Secured $1B+ for Staten Island post-Sandy",
                "Verrazzano Bridge toll reduction advocacy",
                "9/11 first responders funding champion"
            ],
            transition_reason="incumbent",
            predecessor="Daniel Patrick Moynihan"
        )
    ],

    "us_senate_ny_junior": [
        OfficialTenure(
            name="Hillary Clinton",
            position="US Senator (NY Junior)",
            start_date="2001-01-03",
            end_date="2009-01-21",
            party="Democratic",
            election_years=[2000, 2006],
            key_achievements=[
                "9/11 recovery funding",
                "Healthcare advocacy",
                "Armed Services Committee",
                "Economic development focus"
            ],
            transition_reason="moved_to_other_office",  # Secretary of State
            successor="Kirsten Gillibrand"
        ),
        OfficialTenure(
            name="Kirsten Gillibrand",
            position="US Senator (NY Junior)",
            start_date="2009-01-27",  # Appointed to fill Clinton's seat
            end_date="2025-01-03",  # Current
            party="Democratic",
            election_years=[2010, 2012, 2018, 2024],
            key_achievements=[
                "Military sexual assault reform",
                "9/11 health program expansion",
                "Family leave advocacy",
                "Environmental justice focus",
                "Staten Island infrastructure support"
            ],
            transition_reason="incumbent",
            predecessor="Hillary Clinton"
        )
    ],

    "us_house_ny11": [
        OfficialTenure(
            name="Vito Fossella",
            position="US Representative (NY-11)",
            start_date="1997-01-03",  # Started before our period
            end_date="2009-01-03",
            party="Republican",
            election_years=[1997, 1998, 2000, 2002, 2004, 2006],
            key_achievements=[
                "Staten Island Ferry funding",
                "Hurricane Sandy preparation",
                "Transportation infrastructure advocate",
                "9/11 first responders support"
            ],
            transition_reason="retired",  # Personal scandals
            successor="Michael McMahon"
        ),
        OfficialTenure(
            name="Michael McMahon",
            position="US Representative (NY-11)",
            start_date="2009-01-03",
            end_date="2011-01-03",
            party="Democratic",
            election_years=[2008],
            key_achievements=[
                "Healthcare reform support",
                "Small business advocacy",
                "Hurricane preparedness",
                "Veterans affairs focus"
            ],
            transition_reason="defeated",
            predecessor="Vito Fossella",
            successor="Michael Grimm"
        ),
        OfficialTenure(
            name="Michael Grimm",
            position="US Representative (NY-11)",
            start_date="2011-01-03",
            end_date="2015-01-05",  # Resigned
            party="Republican",
            election_years=[2010, 2012, 2014],
            key_achievements=[
                "Hurricane Sandy recovery funding",
                "Small business development",
                "Veterans healthcare",
                "Infrastructure investment"
            ],
            transition_reason="resigned",  # Legal issues
            successor="Daniel Donovan"
        ),
        OfficialTenure(
            name="Daniel Donovan",
            position="US Representative (NY-11)",
            start_date="2015-05-12",  # Special election
            end_date="2019-01-03",
            party="Republican",
            election_years=[2015, 2016],
            key_achievements=[
                "Opioid crisis legislation",
                "Staten Island transportation",
                "Criminal justice reform",
                "Hurricane recovery continuation"
            ],
            transition_reason="defeated",
            predecessor="Michael Grimm",
            successor="Max Rose"
        ),
        OfficialTenure(
            name="Max Rose",
            position="US Representative (NY-11)",
            start_date="2019-01-03",
            end_date="2021-01-03",
            party="Democratic",
            election_years=[2018],
            key_achievements=[
                "Veterans healthcare expansion",
                "Infrastructure modernization",
                "Climate resilience funding",
                "COVID-19 response advocacy"
            ],
            transition_reason="defeated",
            predecessor="Daniel Donovan",
            successor="Nicole Malliotakis"
        ),
        OfficialTenure(
            name="Nicole Malliotakis",
            position="US Representative (NY-11)",
            start_date="2021-01-03",
            end_date="2025-01-03",  # Current
            party="Republican",
            election_years=[2020, 2022, 2024],
            key_achievements=[
                "Congestion pricing opposition",
                "SALT tax deduction advocacy",
                "Border security focus",
                "Small business support",
                "Staten Island Ferry modernization"
            ],
            transition_reason="incumbent",
            predecessor="Max Rose"
        )
    ],

    # ==================== STATE LEVEL ====================

    "ny_senate_district_24": [
        OfficialTenure(
            name="John Marchi",
            position="NY State Senator (District 24)",
            start_date="1957-01-01",  # Long before our period
            end_date="2006-12-31",
            party="Republican",
            election_years=[1956, 1958, 1960, 1962, 1964, 1966, 1968, 1970, 1972, 1974, 1976, 1978, 1980, 1982, 1984, 1986, 1988, 1990, 1992, 1994, 1996, 1998, 2000, 2002, 2004],
            key_achievements=[
                "Dean of the NY Senate (longest serving)",
                "Staten Island transportation advocate",
                "Conservative party influence",
                "Local government champion",
                "49-year tenure record holder"
            ],
            transition_reason="retired",
            successor="Andrew Lanza"
        ),
        OfficialTenure(
            name="Andrew Lanza",
            position="NY State Senator (District 24)",
            start_date="2007-01-01",
            end_date="2025-01-03",  # Current
            party="Republican",
            election_years=[2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
            key_achievements=[
                "Staten Island resiliency funding",
                "Healthcare facility expansion",
                "Transportation infrastructure",
                "Environmental protection",
                "Criminal justice reform",
                "Hurricane Sandy recovery leadership"
            ],
            transition_reason="incumbent",
            predecessor="John Marchi"
        )
    ],

    "ny_assembly_district_61": [
        OfficialTenure(
            name="Vincent Ignizio",
            position="NY Assembly Member (District 61)",
            start_date="2005-01-01",
            end_date="2008-12-31",
            party="Republican",
            election_years=[2004, 2006],
            key_achievements=[
                "Young legislator advocacy",
                "Transportation improvements",
                "Economic development",
                "Healthcare access"
            ],
            transition_reason="moved_to_other_office",  # NYC Council
            successor="Matthew Titone"
        ),
        OfficialTenure(
            name="Matthew Titone",
            position="NY Assembly Member (District 61)",
            start_date="2009-01-01",
            end_date="2025-01-03",  # Current
            party="Democratic",
            election_years=[2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
            key_achievements=[
                "LGBTQ+ rights advocacy",
                "Mental health services",
                "Staten Island healthcare",
                "Transportation funding",
                "Hurricane Sandy recovery"
            ],
            transition_reason="incumbent",
            predecessor="Vincent Ignizio"
        )
    ],

    "ny_assembly_district_62": [
        OfficialTenure(
            name="Lou Tobacco",
            position="NY Assembly Member (District 62)",
            start_date="1995-01-01",
            end_date="2012-12-31",
            party="Republican",
            election_years=[1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010],
            key_achievements=[
                "Veterans services advocate",
                "Transportation infrastructure",
                "Small business support",
                "Staten Island development"
            ],
            transition_reason="defeated",
            successor="Michael Cusick"
        ),
        OfficialTenure(
            name="Michael Cusick",
            position="NY Assembly Member (District 62)",
            start_date="2013-01-01",
            end_date="2025-01-03",  # Current
            party="Democratic",
            election_years=[2012, 2014, 2016, 2018, 2020, 2022, 2024],
            key_achievements=[
                "Public safety initiatives",
                "Healthcare expansion",
                "Economic development",
                "Infrastructure modernization",
                "Hurricane Sandy recovery"
            ],
            transition_reason="incumbent",
            predecessor="Lou Tobacco"
        )
    ],

    "ny_assembly_district_63": [
        OfficialTenure(
            name="Michael Cusick",
            position="NY Assembly Member (District 63)",
            start_date="2003-01-01",
            end_date="2012-12-31",  # Redistricting moved him to 62
            party="Democratic",
            election_years=[2002, 2004, 2006, 2008, 2010],
            key_achievements=[
                "Public safety focus",
                "Economic development",
                "Healthcare advocacy",
                "Transportation improvements"
            ],
            transition_reason="moved_to_other_office",  # Redistricting to District 62
            successor="Ron Castorina Jr."
        ),
        OfficialTenure(
            name="Ron Castorina Jr.",
            position="NY Assembly Member (District 63)",
            start_date="2017-01-01",
            end_date="2020-12-31",
            party="Republican",
            election_years=[2016, 2018],
            key_achievements=[
                "Criminal justice reform",
                "Small business advocacy",
                "Veterans services",
                "Infrastructure development"
            ],
            transition_reason="defeated",
            successor="Charles Fall"
        ),
        OfficialTenure(
            name="Charles Fall",
            position="NY Assembly Member (District 63)",
            start_date="2021-01-01",
            end_date="2025-01-03",  # Current
            party="Democratic",
            election_years=[2020, 2022, 2024],
            key_achievements=[
                "Environmental justice",
                "Healthcare access",
                "Economic development",
                "Climate resilience"
            ],
            transition_reason="incumbent",
            predecessor="Ron Castorina Jr."
        )
    ],

    "ny_assembly_district_64": [
        OfficialTenure(
            name="Robert Straniere",
            position="NY Assembly Member (District 64)",
            start_date="1981-01-01",
            end_date="2004-12-31",
            party="Republican",
            election_years=[1980, 1982, 1984, 1986, 1988, 1990, 1992, 1994, 1996, 1998, 2000, 2002],
            key_achievements=[
                "Judiciary Committee leadership",
                "Legal reform advocacy",
                "Staten Island development",
                "Transportation infrastructure"
            ],
            transition_reason="defeated",
            successor="Joseph Borelli Sr."
        ),
        OfficialTenure(
            name="Joseph Borelli Sr.",
            position="NY Assembly Member (District 64)",
            start_date="2005-01-01",
            end_date="2024-12-31",
            party="Republican",
            election_years=[2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022],
            key_achievements=[
                "Conservative principles advocacy",
                "Small business support",
                "Veterans services",
                "Infrastructure development",
                "Hurricane Sandy recovery"
            ],
            transition_reason="retired",
            successor="Sam Pirozzolo"
        ),
        OfficialTenure(
            name="Sam Pirozzolo",
            position="NY Assembly Member (District 64)",
            start_date="2025-01-01",
            end_date="2025-01-03",  # Current (just elected)
            party="Republican",
            election_years=[2024],
            key_achievements=[
                "Education reform advocacy",
                "Healthcare policy",
                "Business development"
            ],
            transition_reason="incumbent",
            predecessor="Joseph Borelli Sr."
        )
    ],

    # ==================== MUNICIPAL LEVEL ====================

    "nyc_council_district_49": [
        OfficialTenure(
            name="Michael McMahon",
            position="NYC Council Member (District 49)",
            start_date="2002-01-01",
            end_date="2008-12-31",
            party="Democratic",
            election_years=[2001, 2005],
            key_achievements=[
                "North Shore development",
                "Transportation improvements",
                "Public safety initiatives",
                "Economic development"
            ],
            transition_reason="moved_to_other_office",  # US Congress
            successor="Debi Rose"
        ),
        OfficialTenure(
            name="Debi Rose",
            position="NYC Council Member (District 49)",
            start_date="2009-01-01",
            end_date="2021-12-31",
            party="Democratic",
            election_years=[2009, 2013, 2017],
            key_achievements=[
                "North Shore revitalization",
                "Housing development",
                "Healthcare access",
                "Transportation advocacy",
                "Hurricane Sandy recovery"
            ],
            transition_reason="term_limited",
            successor="Kamillah Hanks"
        ),
        OfficialTenure(
            name="Kamillah Hanks",
            position="NYC Council Member (District 49)",
            start_date="2022-01-01",
            end_date="2025-01-03",  # Current
            party="Democratic",
            election_years=[2021],
            key_achievements=[
                "Community development",
                "Public safety focus",
                "Economic opportunity",
                "Youth programs"
            ],
            transition_reason="incumbent",
            predecessor="Debi Rose"
        )
    ],

    "nyc_council_district_50": [
        OfficialTenure(
            name="James Oddo",
            position="NYC Council Member (District 50)",
            start_date="1999-01-01",
            end_date="2013-12-31",
            party="Republican",
            election_years=[1999, 2001, 2005, 2009],
            key_achievements=[
                "Mid-Island advocacy",
                "Transportation infrastructure",
                "Public safety initiatives",
                "Government efficiency",
                "Hurricane Sandy response"
            ],
            transition_reason="moved_to_other_office",  # Staten Island Borough President
            successor="Steven Matteo"
        ),
        OfficialTenure(
            name="Steven Matteo",
            position="NYC Council Member (District 50)",
            start_date="2014-01-01",
            end_date="2021-12-31",
            party="Republican",
            election_years=[2013, 2017],
            key_achievements=[
                "Infrastructure development",
                "Quality of life issues",
                "Business development",
                "Transportation improvements"
            ],
            transition_reason="term_limited",
            successor="David Carr"
        ),
        OfficialTenure(
            name="David Carr",
            position="NYC Council Member (District 50)",
            start_date="2022-01-01",
            end_date="2025-01-03",  # Current
            party="Republican",
            election_years=[2021],
            key_achievements=[
                "Public safety advocacy",
                "Infrastructure modernization",
                "Business support",
                "Quality of life initiatives"
            ],
            transition_reason="incumbent",
            predecessor="Steven Matteo"
        )
    ],

    "nyc_council_district_51": [
        OfficialTenure(
            name="Vincent Ignizio",
            position="NYC Council Member (District 51)",
            start_date="2009-01-01",
            end_date="2017-12-31",
            party="Republican",
            election_years=[2009, 2013],
            key_achievements=[
                "South Shore development",
                "Transportation advocacy",
                "Hurricane Sandy recovery leadership",
                "Economic development",
                "Minority Leader (2014-2017)"
            ],
            transition_reason="term_limited",
            successor="Joe Borelli"
        ),
        OfficialTenure(
            name="Joe Borelli",
            position="NYC Council Member (District 51)",
            start_date="2018-01-01",
            end_date="2025-01-03",  # Current
            party="Republican",
            election_years=[2017, 2021],
            key_achievements=[
                "Conservative advocacy",
                "Public safety focus",
                "Transportation improvements",
                "Business development",
                "Staten Island expressway improvements"
            ],
            transition_reason="incumbent",
            predecessor="Vincent Ignizio"
        )
    ],

    "si_borough_president": [
        OfficialTenure(
            name="Guy Molinari",
            position="Staten Island Borough President",
            start_date="1990-01-01",
            end_date="2001-12-31",
            party="Republican",
            election_years=[1989, 1993, 1997],
            key_achievements=[
                "Staten Island development",
                "Transportation advocacy",
                "Government reform",
                "Economic development"
            ],
            transition_reason="term_limited",
            successor="James Molinaro"
        ),
        OfficialTenure(
            name="James Molinaro",
            position="Staten Island Borough President",
            start_date="2002-01-01",
            end_date="2013-12-31",
            party="Conservative",
            election_years=[2001, 2005, 2009],
            key_achievements=[
                "Transportation infrastructure",
                "Hurricane Sandy recovery",
                "Economic development",
                "Healthcare advocacy",
                "Staten Island Ferry improvements"
            ],
            transition_reason="term_limited",
            successor="James Oddo"
        ),
        OfficialTenure(
            name="James Oddo",
            position="Staten Island Borough President",
            start_date="2014-01-01",
            end_date="2021-12-31",
            party="Republican",
            election_years=[2013, 2017],
            key_achievements=[
                "Hurricane Sandy recovery continuation",
                "Infrastructure modernization",
                "Economic development",
                "Transportation improvements",
                "COVID-19 response leadership"
            ],
            transition_reason="term_limited",
            successor="Vito Fossella"
        ),
        OfficialTenure(
            name="Vito Fossella",
            position="Staten Island Borough President",
            start_date="2022-01-01",
            end_date="2025-01-03",  # Current
            party="Republican",
            election_years=[2021],
            key_achievements=[
                "Economic recovery post-COVID",
                "Infrastructure development",
                "Transportation advocacy",
                "Business development"
            ],
            transition_reason="incumbent",
            predecessor="James Oddo"
        )
    ]
}


def get_official_timeline(position: str, start_year: int = 2000, end_year: int = 2025) -> List[OfficialTenure]:
    """Get chronological timeline of officials for a position within date range."""
    if position not in STATEN_ISLAND_PREDECESSORS:
        return []

    timeline = []
    for tenure in STATEN_ISLAND_PREDECESSORS[position]:
        tenure_start = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
        tenure_end = datetime.strptime(tenure.end_date, "%Y-%m-%d").year

        # Include if tenure overlaps with our date range
        if tenure_end >= start_year and tenure_start <= end_year:
            timeline.append(tenure)

    return sorted(timeline, key=lambda x: x.start_date)


def get_all_predecessors_summary() -> Dict[str, Any]:
    """Get comprehensive summary of all predecessor data."""
    summary = {
        "positions_tracked": len(STATEN_ISLAND_PREDECESSORS),
        "total_officials": 0,
        "party_distribution": {"Democratic": 0, "Republican": 0, "Conservative": 0},
        "transition_reasons": {},
        "longest_tenures": [],
        "position_summaries": {}
    }

    all_tenures = []
    for position, tenures in STATEN_ISLAND_PREDECESSORS.items():
        summary["total_officials"] += len(tenures)

        position_summary = {
            "officials_count": len(tenures),
            "total_years_covered": 0,
            "party_changes": 0,
            "notable_transitions": []
        }

        prev_party = None
        for tenure in tenures:
            all_tenures.append(tenure)

            # Party distribution
            if tenure.party in summary["party_distribution"]:
                summary["party_distribution"][tenure.party] += 1

            # Transition reasons
            if tenure.transition_reason in summary["transition_reasons"]:
                summary["transition_reasons"][tenure.transition_reason] += 1
            else:
                summary["transition_reasons"][tenure.transition_reason] = 1

            # Calculate tenure length
            start_year = datetime.strptime(tenure.start_date, "%Y-%m-%d").year
            end_year = datetime.strptime(tenure.end_date, "%Y-%m-%d").year
            tenure_length = end_year - start_year

            position_summary["total_years_covered"] += tenure_length

            # Track party changes
            if prev_party and prev_party != tenure.party:
                position_summary["party_changes"] += 1
                position_summary["notable_transitions"].append(
                    f"{prev_party} → {tenure.party} ({tenure.name}, {start_year})"
                )
            prev_party = tenure.party

        summary["position_summaries"][position] = position_summary

    # Find longest tenures
    tenure_lengths = [(t.name, t.position,
                      datetime.strptime(t.end_date, "%Y-%m-%d").year -
                      datetime.strptime(t.start_date, "%Y-%m-%d").year)
                     for t in all_tenures]
    summary["longest_tenures"] = sorted(tenure_lengths, key=lambda x: x[2], reverse=True)[:10]

    return summary


def get_electoral_transitions() -> List[Dict[str, Any]]:
    """Get all electoral transitions and their contexts."""
    transitions = []

    for position, tenures in STATEN_ISLAND_PREDECESSORS.items():
        for i, tenure in enumerate(tenures):
            if i > 0:  # Has predecessor
                prev_tenure = tenures[i-1]

                transition = {
                    "position": position,
                    "year": datetime.strptime(tenure.start_date, "%Y-%m-%d").year,
                    "outgoing_official": prev_tenure.name,
                    "outgoing_party": prev_tenure.party,
                    "incoming_official": tenure.name,
                    "incoming_party": tenure.party,
                    "transition_type": tenure.transition_reason,
                    "party_change": prev_tenure.party != tenure.party,
                    "context": {
                        "outgoing_achievements": prev_tenure.key_achievements[-2:],  # Last 2 achievements
                        "incoming_focus": tenure.key_achievements[:2] if tenure.key_achievements else []
                    }
                }
                transitions.append(transition)

    return sorted(transitions, key=lambda x: x["year"])


def analyze_continuity_patterns() -> Dict[str, Any]:
    """Analyze patterns of policy and relationship continuity across transitions."""
    continuity_analysis = {
        "policy_continuity": {},
        "relationship_continuity": {},
        "institutional_memory": {},
        "disruption_events": []
    }

    # Analyze policy focus continuity
    for position, tenures in STATEN_ISLAND_PREDECESSORS.items():
        policy_themes = {}

        for tenure in tenures:
            for achievement in tenure.key_achievements:
                # Extract key themes
                achievement_lower = achievement.lower()
                themes = []

                if any(word in achievement_lower for word in ["transportation", "ferry", "bridge"]):
                    themes.append("transportation")
                if any(word in achievement_lower for word in ["infrastructure", "development"]):
                    themes.append("infrastructure")
                if any(word in achievement_lower for word in ["hurricane", "sandy", "recovery", "resilience"]):
                    themes.append("disaster_recovery")
                if any(word in achievement_lower for word in ["healthcare", "health", "medical"]):
                    themes.append("healthcare")
                if any(word in achievement_lower for word in ["veterans", "military"]):
                    themes.append("veterans")
                if any(word in achievement_lower for word in ["economic", "business", "jobs"]):
                    themes.append("economic_development")

                for theme in themes:
                    if theme not in policy_themes:
                        policy_themes[theme] = []
                    policy_themes[theme].append((tenure.name, tenure.start_date))

        # Calculate continuity scores
        continuity_scores = {}
        for theme, officials in policy_themes.items():
            if len(officials) > 1:
                continuity_scores[theme] = len(officials) / len(tenures)

        continuity_analysis["policy_continuity"][position] = continuity_scores

    # Identify major disruption events
    major_events = [
        {"year": 2001, "event": "9/11 Attacks", "impact": "Emergency response and recovery focus"},
        {"year": 2008, "event": "Financial Crisis", "impact": "Economic recovery and development priorities"},
        {"year": 2012, "event": "Hurricane Sandy", "impact": "Climate resilience and infrastructure hardening"},
        {"year": 2020, "event": "COVID-19 Pandemic", "impact": "Public health and economic recovery"}
    ]

    continuity_analysis["disruption_events"] = major_events

    return continuity_analysis