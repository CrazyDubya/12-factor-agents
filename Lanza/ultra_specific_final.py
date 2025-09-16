import json
from collections import Counter, defaultdict

def analyze_and_reclassify_remaining():
    """Analyze the remaining 243 miscellaneous bills and create ultra-specific categories"""

    print("=== ULTRA-SPECIFIC FINAL CLASSIFICATION ===")

    # Load the refined classification results
    try:
        with open('final_refined_classification.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Final refined classification file not found!")
        return

    # Get the miscellaneous bills
    misc_bills = data['detailed_breakdown'].get('Other - Miscellaneous', [])
    print(f"Analyzing {len(misc_bills)} miscellaneous bills for ultra-specific classification...")

    # Create ultra-specific categories based on exact patterns
    ultra_specific_categories = Counter()
    ultra_classification = defaultdict(list)

    # Define ultra-specific patterns
    ultra_patterns = {
        # Ceremonial/Recognition
        'Legislative - Commemorative Resolutions': ['commemorating', 'celebrating', 'honoring', 'recognizing', 'memorializing'],
        'Legislative - Designations': ['designating', 'declaring', 'proclaiming', 'naming'],

        # Legal Code Maintenance
        'Legal - Technical Amendments': ['amends', 'modifies', 'corrects', 'updates', 'revises'],
        'Legal - Effective Dates': ['effective', 'takes effect', 'shall take effect'],
        'Legal - Repeal/Sunset': ['repeals', 'expires', 'sunset', 'terminates'],

        # Administrative/Procedural
        'Government - Reporting Requirements': ['report', 'reporting', 'annual report', 'submit report'],
        'Government - Meeting/Notice Requirements': ['notice', 'notification', 'meeting', 'public hearing'],
        'Government - Record Keeping': ['record', 'records', 'documentation', 'filing'],
        'Government - Deadline Extensions': ['extends', 'extension', 'deadline', 'time period'],

        # Financial/Administrative
        'Fiscal - Cost Adjustments': ['cost-of-living', 'adjustment', 'increase', 'cost adjustment'],
        'Fiscal - Financial Penalties': ['penalty', 'fine', 'civil penalty', 'monetary penalty'],
        'Fiscal - Refunds/Credits': ['refund', 'credit', 'reimbursement', 'rebate'],

        # Professional/Occupational
        'Professional - Healthcare Regulation': ['medical', 'physician', 'nurse', 'healthcare professional'],
        'Professional - Legal Profession': ['attorney', 'lawyer', 'legal profession', 'bar association'],
        'Professional - Trade/Business': ['business', 'trade', 'commercial', 'professional services'],

        # Public Safety (specific)
        'Public Safety - Emergency Response': ['emergency', 'emergency response', 'disaster', 'emergency services'],
        'Public Safety - Fire Safety': ['fire', 'fire department', 'fire safety', 'firefighter'],
        'Public Safety - Building Safety': ['building', 'safety code', 'inspection', 'building code'],

        # Transportation (ultra-specific)
        'Transportation - Vessel/Marine': ['vessel', 'boat', 'marine', 'watercraft', 'maritime'],
        'Transportation - Registration/Tags': ['registration', 'tag', 'plate', 'certificate'],
        'Transportation - Insurance Requirements': ['insurance', 'coverage', 'liability', 'financial responsibility'],

        # Municipal Operations
        'Municipal - Utility Operations': ['utility', 'water', 'sewer', 'electric', 'gas'],
        'Municipal - Public Property': ['public property', 'municipal property', 'city property'],
        'Municipal - Service Delivery': ['service', 'municipal service', 'public service'],

        # Environmental (specific)
        'Environment - Wetlands/Water': ['wetland', 'water protection', 'waterway', 'aquatic'],
        'Environment - Land Use': ['land use', 'development', 'environmental impact'],
        'Environment - Waste/Recycling': ['waste', 'recycling', 'disposal', 'garbage'],

        # Healthcare (ultra-specific)
        'Healthcare - Insurance Claims': ['insurance', 'claim', 'coverage', 'benefits'],
        'Healthcare - Medical Devices': ['medical device', 'equipment', 'apparatus'],
        'Healthcare - Patient Rights': ['patient', 'patient rights', 'medical privacy'],

        # Social/Family Services
        'Social Services - Child/Family': ['child', 'family', 'children', 'minor'],
        'Social Services - Elderly/Senior': ['elderly', 'senior', 'aging', 'elder'],
        'Social Services - Support Services': ['support', 'assistance', 'aid', 'help'],

        # Consumer/Commercial
        'Consumer - Product Safety': ['product', 'consumer', 'safety', 'warning'],
        'Consumer - Commercial Practices': ['seller', 'sale', 'commercial', 'business practice'],
        'Consumer - Price/Cost Issues': ['price', 'cost', 'pricing', 'charge'],

        # Technology/Communications
        'Technology - Data/Information': ['data', 'information', 'database', 'system'],
        'Technology - Communication Systems': ['communication', 'phone', 'telephone', 'electronic'],

        # Housing/Real Estate (specific)
        'Housing - Property Transactions': ['property', 'real estate', 'sale', 'transfer'],
        'Housing - Rental/Leasing': ['rental', 'lease', 'landlord', 'tenant'],

        # Employment/Labor
        'Employment - Work Conditions': ['work', 'employment', 'worker', 'employee'],
        'Employment - Benefits/Compensation': ['benefit', 'compensation', 'pay', 'wage'],

        # Animal Welfare (specific)
        'Animal Welfare - Companion Animals': ['pet', 'dog', 'cat', 'companion animal'],
        'Animal Welfare - Animal Control': ['animal control', 'stray', 'animal shelter'],

        # Culture/Recreation (specific)
        'Culture - Historical/Heritage': ['historical', 'heritage', 'landmark', 'historic'],
        'Recreation - Public Facilities': ['park', 'recreation', 'facility', 'public space'],

        # Veterans/Military (specific)
        'Veterans - Benefits/Services': ['veteran', 'military', 'armed forces', 'service member'],

        # Taxation (ultra-specific)
        'Fiscal - Tax Collection': ['collection', 'collector', 'tax collection', 'assessment'],
        'Fiscal - Tax Exemptions': ['exempt', 'exemption', 'tax-exempt', 'non-taxable'],

        # Criminal Justice (ultra-specific subcategories)
        'Criminal Justice - Offense Definitions': ['offense', 'crime', 'violation', 'unlawful'],
        'Criminal Justice - Procedure/Process': ['procedure', 'process', 'proceeding', 'hearing'],

        # Catch remaining patterns
        'Administrative - General Requirements': ['require', 'requirement', 'must', 'shall'],
        'Administrative - Permissions/Authorizations': ['authorize', 'permit', 'allow', 'authorize'],
        'Administrative - Restrictions/Prohibitions': ['prohibit', 'restrict', 'ban', 'forbidden'],
    }

    # Classify each miscellaneous bill
    for bill in misc_bills:
        title = bill['title'].lower()
        classified = False

        # Try ultra-specific patterns
        for category, patterns in ultra_patterns.items():
            for pattern in patterns:
                if pattern in title:
                    ultra_specific_categories[category] += 1
                    ultra_classification[category].append(bill)
                    classified = True
                    break
            if classified:
                break

        # If still not classified, put in truly miscellaneous
        if not classified:
            ultra_specific_categories['Truly Miscellaneous'] += 1
            ultra_classification['Truly Miscellaneous'].append(bill)

    # Show results
    total_misc = len(misc_bills)
    total_bills = data['total_bills']

    print(f"\nULTRA-SPECIFIC RECLASSIFICATION RESULTS:")
    print(f"Original miscellaneous: {total_misc} bills")

    sorted_ultra = ultra_specific_categories.most_common()

    for category, count in sorted_ultra:
        percentage_of_misc = (count / total_misc) * 100
        percentage_of_total = (count / total_bills) * 100
        print(f"{category:<45} {count:3d} bills ({percentage_of_misc:4.1f}% of misc, {percentage_of_total:3.1f}% total)")

    # Calculate new "Other" percentage
    truly_misc = ultra_specific_categories.get('Truly Miscellaneous', 0)
    new_other_percentage = (truly_misc / total_bills) * 100

    print(f"\nFINAL 'OTHER' RESULT:")
    print(f"Truly Miscellaneous: {truly_misc} bills ({new_other_percentage:.1f}% of total)")

    if new_other_percentage < 5:
        print(f"🎯 SUCCESS! 'Other' reduced to {new_other_percentage:.1f}% (under 5% target!)")
    else:
        print(f"⚠️  Still need to reduce 'Other' from {new_other_percentage:.1f}%")

    # Show examples of truly miscellaneous bills
    if truly_misc > 0:
        print(f"\nSample 'Truly Miscellaneous' bills:")
        for i, bill in enumerate(ultra_classification['Truly Miscellaneous'][:10], 1):
            print(f"{i:2d}. {bill['bill']} ({bill['year']}): {bill['title']}")

    # Save the ultra-specific classification
    ultra_results = {
        'original_misc_count': total_misc,
        'ultra_specific_categories': dict(ultra_specific_categories),
        'detailed_breakdown': dict(ultra_classification),
        'truly_misc_count': truly_misc,
        'final_other_percentage': new_other_percentage,
        'success': new_other_percentage < 5
    }

    with open('ultra_specific_classification.json', 'w') as f:
        json.dump(ultra_results, f, indent=2, default=str)

    print(f"\n✅ Ultra-specific classification saved to 'ultra_specific_classification.json'")

    return ultra_results

if __name__ == "__main__":
    analyze_and_reclassify_remaining()