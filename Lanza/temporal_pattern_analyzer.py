import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
import warnings
warnings.filterwarnings('ignore')

# Try to import advanced time series libraries
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from scipy import stats
    from scipy.signal import find_peaks
    HAS_ADVANCED_LIBS = True
except ImportError:
    HAS_ADVANCED_LIBS = False
    print("Advanced time series libraries not available. Install with: pip install statsmodels scipy")

def load_comprehensive_data():
    """Load all available Lanza data"""

    datasets = {}

    # Load comprehensive involvement data
    try:
        with open('comprehensive_lanza_involvement.json', 'r') as f:
            datasets['involvement'] = json.load(f)
    except FileNotFoundError:
        print("Warning: comprehensive_lanza_involvement.json not found")
        datasets['involvement'] = None

    # Load 19-year analysis
    try:
        with open('comprehensive_19_year_lanza_analysis.json', 'r') as f:
            datasets['career'] = json.load(f)
    except FileNotFoundError:
        print("Warning: comprehensive_19_year_lanza_analysis.json not found")
        datasets['career'] = None

    return datasets

def create_temporal_dataset(datasets):
    """Create comprehensive temporal dataset"""

    all_bills = []

    # Extract bills from involvement data
    if datasets['involvement']:
        all_bills.extend(datasets['involvement'].get('all_bills_found', []))

    # Extract bills from career data
    if datasets['career']:
        for session_data in datasets['career'].get('session_data', {}).values():
            all_bills.extend(session_data.get('bills_sponsored', []))

    # Remove duplicates by bill ID
    unique_bills = {}
    for bill in all_bills:
        if isinstance(bill, dict):
            bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
            if bill_id not in unique_bills:
                unique_bills[bill_id] = bill

    print(f"Processing {len(unique_bills)} unique bills")

    # Convert to structured data
    temporal_data = []

    for bill_id, bill in unique_bills.items():
        try:
            # Extract temporal features
            publish_date = bill.get('publishedDateTime', '')
            session = bill.get('session', 0)
            title = bill.get('title', '')
            status = bill.get('status', {})

            # Parse date
            if publish_date and publish_date != '2009-01-01T00:00:01':  # Skip placeholder dates
                try:
                    if 'T' in publish_date:
                        date_obj = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    else:
                        date_obj = datetime.strptime(publish_date, '%Y-%m-%d')
                except:
                    date_obj = datetime(session if session > 2000 else 2009, 1, 1)  # Default
            else:
                date_obj = datetime(session if session > 2000 else 2009, 1, 1)

            # Extract features
            bill_data = {
                'bill_id': bill_id,
                'bill_number': bill.get('basePrintNo', ''),
                'session': session,
                'publish_date': date_obj,
                'year': date_obj.year,
                'month': date_obj.month,
                'day_of_year': date_obj.timetuple().tm_yday,
                'quarter': (date_obj.month - 1) // 3 + 1,
                'title': title,
                'title_length': len(title),
                'word_count': len(title.split()) if title else 0,
                'status_type': status.get('statusType', 'UNKNOWN'),
                'status_desc': status.get('statusDesc', ''),
                'committee': status.get('committeeName', ''),
                'action_date': status.get('actionDate', ''),
                'signed': bill.get('signed', False),
                'adopted': bill.get('adopted', False),
                'vetoed': bill.get('vetoed', False)
            }

            # Policy classification
            title_lower = title.lower()
            if any(term in title_lower for term in ['trafficking', 'victim', 'exploitation']):
                bill_data['policy_area'] = 'Human Trafficking'
            elif any(term in title_lower for term in ['animal', 'companion', 'pet']):
                bill_data['policy_area'] = 'Animal Welfare'
            elif any(term in title_lower for term in ['license', 'driver', 'fee', 'vehicle']):
                bill_data['policy_area'] = 'Transportation'
            elif any(term in title_lower for term in ['crime', 'criminal', 'penalty']):
                bill_data['policy_area'] = 'Criminal Justice'
            elif any(term in title_lower for term in ['health', 'medical', 'insurance']):
                bill_data['policy_area'] = 'Healthcare'
            elif any(term in title_lower for term in ['education', 'school', 'student']):
                bill_data['policy_area'] = 'Education'
            elif any(term in title_lower for term in ['tax', 'revenue', 'budget']):
                bill_data['policy_area'] = 'Fiscal'
            elif any(term in title_lower for term in ['environment', 'conservation']):
                bill_data['policy_area'] = 'Environmental'
            elif any(term in title_lower for term in ['senior', 'elderly', 'aging']):
                bill_data['policy_area'] = 'Senior Issues'
            elif any(term in title_lower for term in ['housing', 'rent', 'tenant']):
                bill_data['policy_area'] = 'Housing'
            else:
                bill_data['policy_area'] = 'Other'

            # Success metrics
            bill_data['success_score'] = 0
            if bill_data['signed']:
                bill_data['success_score'] = 3
            elif 'signed' in bill_data['status_desc'].lower():
                bill_data['success_score'] = 3
            elif bill_data['status_type'] in ['PASSED_SENATE', 'PASSED_ASSEMBLY']:
                bill_data['success_score'] = 2
            elif 'floor' in bill_data['status_desc'].lower():
                bill_data['success_score'] = 1

            temporal_data.append(bill_data)

        except Exception as e:
            print(f"Error processing bill {bill_id}: {e}")

    return pd.DataFrame(temporal_data)

def analyze_temporal_patterns(df):
    """Comprehensive temporal pattern analysis"""

    print("=== TEMPORAL PATTERN ANALYSIS ===")

    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'data_summary': {
            'total_bills': len(df),
            'date_range': f"{df['year'].min()} - {df['year'].max()}",
            'sessions': sorted(df['session'].unique().tolist()),
            'policy_areas': df['policy_area'].value_counts().to_dict()
        },
        'temporal_insights': {},
        'anomalies': [],
        'predictions': {}
    }

    # 1. Yearly Activity Analysis
    yearly_activity = df.groupby('year').agg({
        'bill_id': 'count',
        'success_score': ['mean', 'sum'],
        'policy_area': lambda x: x.mode().iloc[0] if len(x) > 0 else 'None'
    }).round(3)

    yearly_activity.columns = ['bill_count', 'avg_success', 'total_success', 'dominant_policy']

    print(f"Yearly Activity Pattern:")
    print(yearly_activity)

    analysis_results['temporal_insights']['yearly_activity'] = yearly_activity.to_dict()

    # 2. Session Analysis
    session_activity = df.groupby('session').agg({
        'bill_id': 'count',
        'success_score': 'mean',
        'policy_area': lambda x: x.value_counts().to_dict() if len(x) > 0 else {}
    }).round(3)

    print(f"\nSession Activity:")
    print(session_activity)

    # 3. Seasonal Patterns
    monthly_patterns = df.groupby('month')['bill_id'].count()
    quarterly_patterns = df.groupby('quarter')['bill_id'].count()

    print(f"\nMonthly Introduction Pattern:")
    print(monthly_patterns)

    print(f"\nQuarterly Pattern:")
    print(quarterly_patterns)

    analysis_results['temporal_insights']['seasonal'] = {
        'monthly': monthly_patterns.to_dict(),
        'quarterly': quarterly_patterns.to_dict()
    }

    # 4. Policy Area Evolution
    policy_evolution = df.groupby(['year', 'policy_area']).size().unstack(fill_value=0)

    print(f"\nPolicy Area Evolution:")
    print(policy_evolution)

    analysis_results['temporal_insights']['policy_evolution'] = policy_evolution.to_dict()

    # 5. Anomaly Detection

    # Detect activity spikes
    yearly_counts = df.groupby('year')['bill_id'].count()
    mean_activity = yearly_counts.mean()
    std_activity = yearly_counts.std()

    anomaly_threshold = mean_activity + 2 * std_activity
    anomalous_years = yearly_counts[yearly_counts > anomaly_threshold]

    if len(anomalous_years) > 0:
        for year, count in anomalous_years.items():
            anomaly = {
                'type': 'Activity Spike',
                'year': int(year),
                'bill_count': int(count),
                'expected_range': f"{mean_activity:.1f} ± {2*std_activity:.1f}",
                'z_score': float((count - mean_activity) / std_activity),
                'description': f"Unusual spike of {count} bills in {year} (normal: {mean_activity:.1f})"
            }
            analysis_results['anomalies'].append(anomaly)
            print(f"\n🚨 ANOMALY DETECTED: {anomaly['description']}")

    # Detect policy shifts
    dominant_policies_by_year = df.groupby('year')['policy_area'].agg(lambda x: x.value_counts().index[0] if len(x) > 0 else 'None')
    policy_shifts = []

    prev_policy = None
    for year, policy in dominant_policies_by_year.items():
        if prev_policy and policy != prev_policy:
            policy_shifts.append({
                'year': int(year),
                'from_policy': prev_policy,
                'to_policy': policy
            })
        prev_policy = policy

    if policy_shifts:
        for shift in policy_shifts:
            anomaly = {
                'type': 'Policy Shift',
                'year': shift['year'],
                'from_policy': shift['from_policy'],
                'to_policy': shift['to_policy'],
                'description': f"Policy focus shifted from {shift['from_policy']} to {shift['to_policy']} in {shift['year']}"
            }
            analysis_results['anomalies'].append(anomaly)
            print(f"📈 POLICY SHIFT: {anomaly['description']}")

    # 6. Advanced Time Series Analysis (if libraries available)
    if HAS_ADVANCED_LIBS and len(df) > 10:

        # Create time series
        df_ts = df.set_index('publish_date').sort_index()

        # Monthly aggregation
        monthly_ts = df_ts.resample('M')['bill_id'].count()

        if len(monthly_ts) > 12:  # Need enough data for seasonal decomposition
            try:
                # Seasonal decomposition
                decomposition = seasonal_decompose(monthly_ts, model='additive', period=12)

                analysis_results['temporal_insights']['seasonal_decomposition'] = {
                    'trend': decomposition.trend.dropna().to_dict(),
                    'seasonal': decomposition.seasonal.dropna().to_dict(),
                    'residual': decomposition.resid.dropna().to_dict()
                }

                print(f"\n📊 Seasonal Decomposition completed")

            except Exception as e:
                print(f"Seasonal decomposition failed: {e}")

        # Trend analysis
        years = df.groupby('year')['bill_id'].count()
        if len(years) > 3:
            slope, intercept, r_value, p_value, std_err = stats.linregress(years.index, years.values)

            trend_analysis = {
                'slope': float(slope),
                'r_squared': float(r_value**2),
                'p_value': float(p_value),
                'trend_description': 'Increasing' if slope > 0 else 'Decreasing' if slope < 0 else 'Stable'
            }

            analysis_results['temporal_insights']['trend_analysis'] = trend_analysis
            print(f"\n📈 Long-term trend: {trend_analysis['trend_description']} (R² = {trend_analysis['r_squared']:.3f})")

    # 7. Career Phase Analysis
    career_phases = []
    years_sorted = sorted(df['year'].unique())

    if len(years_sorted) >= 3:
        # Divide career into phases
        total_years = len(years_sorted)
        early_years = years_sorted[:total_years//3]
        middle_years = years_sorted[total_years//3:2*total_years//3]
        late_years = years_sorted[2*total_years//3:]

        for phase_name, phase_years in [('Early Career', early_years),
                                      ('Mid Career', middle_years),
                                      ('Late Career', late_years)]:
            if phase_years:
                phase_data = df[df['year'].isin(phase_years)]

                phase_analysis = {
                    'phase': phase_name,
                    'years': phase_years,
                    'total_bills': len(phase_data),
                    'avg_bills_per_year': len(phase_data) / len(phase_years),
                    'success_rate': phase_data['success_score'].mean(),
                    'top_policy_areas': phase_data['policy_area'].value_counts().head(3).to_dict(),
                    'productivity_score': len(phase_data) * phase_data['success_score'].mean()
                }

                career_phases.append(phase_analysis)
                print(f"\n{phase_name} ({min(phase_years)}-{max(phase_years)}):")
                print(f"  Bills: {phase_analysis['total_bills']} ({phase_analysis['avg_bills_per_year']:.1f}/year)")
                print(f"  Success Rate: {phase_analysis['success_rate']:.2f}")
                print(f"  Top Policies: {list(phase_analysis['top_policy_areas'].keys())[:3]}")

    analysis_results['temporal_insights']['career_phases'] = career_phases

    return analysis_results

def visualize_patterns(df, analysis_results):
    """Create visualizations for temporal patterns"""

    # Set up plotting style
    plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')

    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Senator Lanza: Temporal Legislative Patterns (2007-2025)', fontsize=16, fontweight='bold')

    # 1. Bills per year
    yearly = df.groupby('year')['bill_id'].count()
    axes[0,0].bar(yearly.index, yearly.values, color='steelblue', alpha=0.7)
    axes[0,0].set_title('Bills Introduced Per Year')
    axes[0,0].set_xlabel('Year')
    axes[0,0].set_ylabel('Number of Bills')
    axes[0,0].tick_params(axis='x', rotation=45)

    # Add anomaly markers
    for anomaly in analysis_results['anomalies']:
        if anomaly['type'] == 'Activity Spike':
            axes[0,0].axvline(x=anomaly['year'], color='red', linestyle='--', alpha=0.7)
            axes[0,0].text(anomaly['year'], anomaly['bill_count'], 'SPIKE',
                          rotation=90, color='red', fontweight='bold')

    # 2. Policy areas over time
    policy_evolution = df.groupby(['year', 'policy_area']).size().unstack(fill_value=0)
    policy_evolution.plot(kind='area', stacked=True, ax=axes[0,1], alpha=0.7)
    axes[0,1].set_title('Policy Focus Evolution')
    axes[0,1].set_xlabel('Year')
    axes[0,1].set_ylabel('Number of Bills')
    axes[0,1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

    # 3. Success rate over time
    yearly_success = df.groupby('year')['success_score'].mean()
    axes[0,2].plot(yearly_success.index, yearly_success.values, marker='o', linewidth=2, color='green')
    axes[0,2].set_title('Legislative Success Rate Over Time')
    axes[0,2].set_xlabel('Year')
    axes[0,2].set_ylabel('Average Success Score')
    axes[0,2].tick_params(axis='x', rotation=45)

    # 4. Seasonal patterns
    monthly = df.groupby('month')['bill_id'].count()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    axes[1,0].bar(range(1, 13), monthly.reindex(range(1, 13), fill_value=0), color='orange', alpha=0.7)
    axes[1,0].set_title('Bills by Month (Seasonal Pattern)')
    axes[1,0].set_xlabel('Month')
    axes[1,0].set_ylabel('Number of Bills')
    axes[1,0].set_xticks(range(1, 13))
    axes[1,0].set_xticklabels(month_names)

    # 5. Policy area distribution
    policy_counts = df['policy_area'].value_counts()
    axes[1,1].pie(policy_counts.values, labels=policy_counts.index, autopct='%1.1f%%', startangle=90)
    axes[1,1].set_title('Overall Policy Area Distribution')

    # 6. Career phases comparison
    if 'career_phases' in analysis_results['temporal_insights']:
        phases = analysis_results['temporal_insights']['career_phases']
        phase_names = [p['phase'] for p in phases]
        phase_productivity = [p['productivity_score'] for p in phases]

        axes[1,2].bar(phase_names, phase_productivity, color=['lightblue', 'lightgreen', 'lightcoral'])
        axes[1,2].set_title('Productivity by Career Phase')
        axes[1,2].set_ylabel('Productivity Score')
        axes[1,2].tick_params(axis='x', rotation=45)
    else:
        axes[1,2].text(0.5, 0.5, 'Insufficient data\nfor career phases',
                      ha='center', va='center', transform=axes[1,2].transAxes)
        axes[1,2].set_title('Career Phases Analysis')

    plt.tight_layout()
    plt.savefig('lanza_temporal_patterns.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("📊 Visualization saved as 'lanza_temporal_patterns.png'")

def main():
    """Main analysis function"""

    print("=== LANZA TEMPORAL PATTERN ANALYZER ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Load data
    datasets = load_comprehensive_data()

    if not any(datasets.values()):
        print("❌ No data found. Please run data harvesting scripts first.")
        return

    # Create temporal dataset
    df = create_temporal_dataset(datasets)

    if df.empty:
        print("❌ No temporal data could be extracted.")
        return

    print(f"✅ Created temporal dataset with {len(df)} bills")
    print(f"Date range: {df['year'].min()} - {df['year'].max()}")
    print(f"Policy areas: {df['policy_area'].nunique()}")
    print()

    # Analyze patterns
    analysis_results = analyze_temporal_patterns(df)

    # Create visualizations
    try:
        visualize_patterns(df, analysis_results)
    except Exception as e:
        print(f"Visualization failed: {e}")

    # Save analysis
    with open('temporal_pattern_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print(f"\n✅ Temporal pattern analysis complete!")
    print(f"✅ Results saved to 'temporal_pattern_analysis.json'")

    # Summary insights
    print(f"\n=== KEY INSIGHTS ===")
    print(f"🔢 Total legislative activity: {analysis_results['data_summary']['total_bills']} bills")
    print(f"📅 Active period: {analysis_results['data_summary']['date_range']}")
    print(f"🏛️ Sessions covered: {len(analysis_results['data_summary']['sessions'])}")
    print(f"📊 Policy areas: {len(analysis_results['data_summary']['policy_areas'])}")

    if analysis_results['anomalies']:
        print(f"\n🚨 {len(analysis_results['anomalies'])} anomalies detected:")
        for anomaly in analysis_results['anomalies']:
            print(f"   • {anomaly['description']}")

    return analysis_results, df

if __name__ == "__main__":
    main()