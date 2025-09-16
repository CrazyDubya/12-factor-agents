import json
from collections import Counter

def analyze_unclassified_bills():
    """Analyze the unclassified bills to create more specific categories"""

    print("=== ANALYZING UNCLASSIFIED BILLS ===")

    # Load the ultra-granular classification results
    try:
        with open('ultra_granular_classification.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Ultra-granular classification file not found!")
        return

    unclassified_bills = data['detailed_breakdown'].get('Other - Unclassified', [])

    print(f"Found {len(unclassified_bills)} unclassified bills")
    print("\nSample unclassified bills for pattern analysis:")

    # Analyze patterns in unclassified bills
    title_words = Counter()

    for i, bill in enumerate(unclassified_bills[:50]):  # Show first 50
        title = bill['title'].lower()
        words = title.split()

        # Count important words
        for word in words:
            if len(word) > 3 and word not in ['bills', 'acts', 'laws', 'the', 'and', 'for', 'with', 'that', 'this', 'from', 'such', 'shall', 'would', 'chapter']:
                title_words[word] += 1

        print(f"{i+1:2d}. {bill['bill']} ({bill['year']}): {bill['title']}")

    print(f"\n=== MOST COMMON WORDS IN UNCLASSIFIED BILLS ===")
    print("Top 30 words that could help create new categories:")

    for word, count in title_words.most_common(30):
        percentage = (count / len(unclassified_bills)) * 100
        print(f"{word:<20} {count:3d} occurrences ({percentage:4.1f}%)")

    # Suggest new categories based on patterns
    print(f"\n=== SUGGESTED NEW CATEGORIES ===")

    suggested_categories = {
        'Legal - Code Revision': ['amends', 'modifies', 'revises', 'updates', 'section'],
        'Municipal - Water/Sewer': ['water', 'sewer', 'wastewater', 'utility', 'rates'],
        'Municipal - Public Works': ['public', 'works', 'infrastructure', 'maintenance'],
        'Professional - Licensing': ['license', 'certification', 'professional', 'practice'],
        'Housing - Development': ['development', 'housing', 'residential', 'zoning'],
        'Municipal - Services': ['services', 'municipal', 'city', 'county', 'local'],
        'Legal - Procedures': ['procedures', 'process', 'requirements', 'standards'],
        'Financial - Fees': ['fees', 'charges', 'costs', 'expenses', 'payment'],
        'Public - Administration': ['administration', 'administrative', 'management', 'operations'],
        'Legal - Definitions': ['defines', 'definition', 'meaning', 'terms', 'definitions'],
    }

    for category, keywords in suggested_categories.items():
        matching_bills = []
        for bill in unclassified_bills:
            title = bill['title'].lower()
            if any(keyword in title for keyword in keywords):
                matching_bills.append(bill)

        if matching_bills:
            percentage = (len(matching_bills) / len(unclassified_bills)) * 100
            print(f"{category:<30} {len(matching_bills):3d} bills ({percentage:4.1f}%)")

            # Show examples
            for bill in matching_bills[:3]:
                print(f"  Example: {bill['bill']} - {bill['title'][:80]}...")

    print(f"\n=== YEAR DISTRIBUTION OF UNCLASSIFIED BILLS ===")
    year_dist = Counter(bill['year'] for bill in unclassified_bills)
    for year, count in sorted(year_dist.items()):
        percentage = (count / len(unclassified_bills)) * 100
        print(f"{year}: {count:3d} bills ({percentage:4.1f}%)")

if __name__ == "__main__":
    analyze_unclassified_bills()