import requests
import json
from datetime import datetime
from collections import Counter, defaultdict
import time

API_KEY = "gNyGkkPgvKrEKXaq7OehFL5D65t4S7yM"
BASE_URL = "https://legislation.nysenate.gov/api/3"

def get_all_sessions():
    """Get all available sessions from 2007-2025"""
    # Lanza entered Senate in 2007
    sessions = list(range(2007, 2026, 2))  # Odd years are session years
    return sessions

def search_member_bills(session, member_id=409, limit=1000):
    """Search for all bills by Lanza in a specific session"""
    # Try multiple search strategies
    strategies = [
        f"{BASE_URL}/bills/{session}",
        f"{BASE_URL}/bills/search",
        f"{BASE_URL}/members/{member_id}/bills/{session}"
    ]

    params_list = [
        {"key": API_KEY, "limit": limit, "sponsor": "lanza"},
        {"key": API_KEY, "limit": limit, "term": f"session:{session} sponsor:lanza"},
        {"key": API_KEY}
    ]

    all_bills = []

    for i, (url, params) in enumerate(zip(strategies, params_list)):
        try:
            print(f"  Strategy {i+1}: {url}")
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    # Handle different response structures
                    if 'result' in data:
                        if 'items' in data['result']:
                            bills = data['result']['items']
                        else:
                            bills = [data['result']] if isinstance(data['result'], dict) else []
                    else:
                        bills = data if isinstance(data, list) else []

                    # Filter for Lanza as primary sponsor
                    lanza_bills = []
                    for bill in bills:
                        if isinstance(bill, dict):
                            sponsor = bill.get('sponsor', {})
                            if sponsor:
                                member = sponsor.get('member', {})
                                if member and ('lanza' in member.get('fullName', '').lower() or
                                             member.get('memberId') == 409):
                                    lanza_bills.append(bill)

                    print(f"    Found {len(lanza_bills)} Lanza bills")
                    all_bills.extend(lanza_bills)

                    if lanza_bills:
                        break  # Use first successful strategy

            else:
                print(f"    Status: {response.status_code}")

        except Exception as e:
            print(f"    Error: {e}")

    return all_bills

def get_voting_records(session, member_id=409):
    """Get voting records for Lanza in a specific session"""
    try:
        url = f"{BASE_URL}/members/{member_id}/votes/{session}"
        response = requests.get(url, params={"key": API_KEY}, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('result', {}).get('items', [])

    except Exception as e:
        print(f"    Voting records error: {e}")

    return []

def get_committee_assignments(session, member_id=409):
    """Get committee assignments for a session"""
    try:
        url = f"{BASE_URL}/members/{member_id}"
        response = requests.get(url, params={"key": API_KEY, "sessionYear": session}, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                member_data = data.get('result', {})
                # Look for committee information in member data
                return member_data.get('committees', [])

    except Exception as e:
        print(f"    Committee assignment error: {e}")

    return []

def comprehensive_19_year_analysis():
    """Comprehensive analysis of Lanza's entire 19-year Senate career"""

    print("=== COMPREHENSIVE 19-YEAR LANZA SENATE ANALYSIS ===")
    print(f"Timestamp: {datetime.now()}")
    print("Analyzing Senator Lanza's complete legislative record (2007-2025)")
    print()

    sessions = get_all_sessions()
    print(f"Sessions to analyze: {sessions}")
    print()

    comprehensive_data = {
        'analysis_timestamp': datetime.now().isoformat(),
        'senator_info': {
            'name': 'Andrew J. Lanza',
            'member_id': 409,
            'service_period': '2007-2025',
            'total_sessions': len(sessions)
        },
        'session_data': {},
        'career_summary': {
            'total_bills_sponsored': 0,
            'bills_signed_into_law': 0,
            'primary_policy_areas': Counter(),
            'committee_history': [],
            'voting_patterns': {},
            'legislative_partnerships': {},
            'career_evolution': []
        }
    }

    all_bills = []
    all_votes = []

    # Analyze each session
    for session in sessions:
        print(f"=== SESSION {session} ===")
        session_data = {
            'session_year': session,
            'bills_sponsored': [],
            'votes_cast': [],
            'committee_assignments': [],
            'session_summary': {}
        }

        # Get bills for this session
        print(f"Searching bills for {session}:")
        bills = search_member_bills(session)
        session_data['bills_sponsored'] = bills
        all_bills.extend(bills)

        print(f"Searching votes for {session}:")
        votes = get_voting_records(session)
        session_data['votes_cast'] = votes
        all_votes.extend(votes)

        print(f"Getting committee assignments for {session}:")
        committees = get_committee_assignments(session)
        session_data['committee_assignments'] = committees

        # Session summary
        session_data['session_summary'] = {
            'bills_count': len(bills),
            'votes_count': len(votes),
            'committees_count': len(committees)
        }

        comprehensive_data['session_data'][str(session)] = session_data

        print(f"Session {session} complete: {len(bills)} bills, {len(votes)} votes, {len(committees)} committees")
        print()

        # Rate limiting
        time.sleep(1)

    # Comprehensive career analysis
    print("=== CAREER ANALYSIS ===")

    # Bill analysis
    comprehensive_data['career_summary']['total_bills_sponsored'] = len(all_bills)

    # Policy area analysis
    policy_areas = Counter()
    bills_by_status = Counter()
    bills_by_committee = Counter()
    bills_signed = []

    for bill in all_bills:
        # Policy classification
        title = bill.get('title', '').lower()

        if any(term in title for term in ['trafficking', 'victim', 'exploitation']):
            policy_areas['Human Trafficking'] += 1
        elif any(term in title for term in ['animal', 'companion', 'pet', 'welfare']):
            policy_areas['Animal Welfare'] += 1
        elif any(term in title for term in ['license', 'driver', 'fee', 'motor', 'vehicle']):
            policy_areas['Transportation/Consumer Protection'] += 1
        elif any(term in title for term in ['crime', 'criminal', 'penalty', 'sentence']):
            policy_areas['Criminal Justice'] += 1
        elif any(term in title for term in ['health', 'medical', 'insurance', 'care']):
            policy_areas['Healthcare'] += 1
        elif any(term in title for term in ['education', 'school', 'student', 'teacher']):
            policy_areas['Education'] += 1
        elif any(term in title for term in ['tax', 'revenue', 'budget', 'fiscal']):
            policy_areas['Fiscal Policy'] += 1
        elif any(term in title for term in ['environment', 'conservation', 'pollution']):
            policy_areas['Environmental'] += 1
        else:
            policy_areas['Other'] += 1

        # Status analysis
        status = bill.get('status', {})
        status_type = status.get('statusType', 'Unknown')
        bills_by_status[status_type] += 1

        if status_type == 'SIGNED_BY_GOVERNOR' or 'signed' in status.get('statusDesc', '').lower():
            bills_signed.append(bill)

        # Committee analysis
        committee = status.get('committeeName')
        if committee:
            bills_by_committee[committee] += 1

    comprehensive_data['career_summary']['primary_policy_areas'] = dict(policy_areas.most_common(10))
    comprehensive_data['career_summary']['bills_signed_into_law'] = len(bills_signed)
    comprehensive_data['career_summary']['bills_by_status'] = dict(bills_by_status)
    comprehensive_data['career_summary']['bills_by_committee'] = dict(bills_by_committee.most_common(10))
    comprehensive_data['career_summary']['signed_bills'] = bills_signed

    # Voting pattern analysis (if we have vote data)
    if all_votes:
        voting_patterns = {
            'total_votes': len(all_votes),
            'vote_distribution': Counter(),
            'party_line_voting': 0,
            'bipartisan_votes': 0
        }

        for vote in all_votes:
            vote_type = vote.get('memberVote', {}).get('vote')
            if vote_type:
                voting_patterns['vote_distribution'][vote_type] += 1

        comprehensive_data['career_summary']['voting_patterns'] = voting_patterns

    # Career evolution analysis
    career_evolution = []
    for session in sessions:
        session_str = str(session)
        if session_str in comprehensive_data['session_data']:
            session_info = comprehensive_data['session_data'][session_str]
            career_evolution.append({
                'session': session,
                'bills_sponsored': len(session_info['bills_sponsored']),
                'major_themes': [],  # Could analyze themes per session
                'productivity_score': len(session_info['bills_sponsored']) + len(session_info['votes_cast'])/10
            })

    comprehensive_data['career_summary']['career_evolution'] = career_evolution

    # Save comprehensive analysis
    filename = 'comprehensive_19_year_lanza_analysis.json'
    with open(filename, 'w') as f:
        json.dump(comprehensive_data, f, indent=2, default=str)

    # Print summary
    print("=== 19-YEAR CAREER SUMMARY ===")
    print(f"✓ Total sessions analyzed: {len(sessions)}")
    print(f"✓ Total bills sponsored: {len(all_bills)}")
    print(f"✓ Bills signed into law: {len(bills_signed)}")
    print(f"✓ Total votes analyzed: {len(all_votes)}")
    print(f"✓ Top policy areas: {', '.join([k for k, v in policy_areas.most_common(5)])}")
    print(f"✓ Most active committees: {', '.join([k for k, v in bills_by_committee.most_common(3)])}")
    print(f"✓ Saved comprehensive analysis to {filename}")

    return comprehensive_data

if __name__ == "__main__":
    comprehensive_19_year_analysis()