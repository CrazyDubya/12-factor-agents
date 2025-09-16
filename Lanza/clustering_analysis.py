import json
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Machine Learning libraries
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering
from sklearn.decomposition import PCA, TruncatedSVD, FactorAnalysis
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.mixture import GaussianMixture

import warnings
warnings.filterwarnings('ignore')

def load_comprehensive_data():
    """Load all available data for clustering analysis"""

    print("Loading comprehensive data for clustering analysis...")

    datasets = {}

    # Load comprehensive involvement data
    try:
        with open('comprehensive_lanza_involvement.json', 'r') as f:
            datasets['involvement'] = json.load(f)
    except FileNotFoundError:
        print("Warning: comprehensive_lanza_involvement.json not found")

    # Load temporal analysis
    try:
        with open('temporal_pattern_analysis.json', 'r') as f:
            datasets['temporal'] = json.load(f)
    except FileNotFoundError:
        print("Warning: temporal_pattern_analysis.json not found")

    # Load NLP analysis
    try:
        with open('nlp_policy_analysis.json', 'r') as f:
            datasets['nlp'] = json.load(f)
    except FileNotFoundError:
        print("Warning: nlp_policy_analysis.json not found")

    return datasets

def create_multi_dimensional_dataset(datasets):
    """Create comprehensive multi-dimensional dataset for clustering"""

    print("Creating multi-dimensional feature dataset...")

    all_bills = []

    # Extract bills from involvement data
    if datasets.get('involvement'):
        all_bills.extend(datasets['involvement'].get('all_bills_found', []))

    if not all_bills:
        print("No bill data found for clustering")
        return pd.DataFrame()

    # Remove duplicates
    unique_bills = {}
    for bill in all_bills:
        if isinstance(bill, dict):
            bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"
            if bill_id not in unique_bills:
                unique_bills[bill_id] = bill

    print(f"Processing {len(unique_bills)} unique bills")

    # Create comprehensive feature set
    clustering_data = []

    for bill_id, bill in unique_bills.items():
        try:
            # Basic features
            features = {
                'bill_id': bill_id,
                'bill_number': bill.get('basePrintNo', ''),
                'session': bill.get('session', 0),
                'year': bill.get('session', 0)  # Use session as year proxy
            }

            # Text-based features
            title = bill.get('title', '')
            summary = bill.get('summary', '')
            all_text = f"{title} {summary}".strip()

            features.update({
                'title_length': len(title),
                'summary_length': len(summary),
                'total_text_length': len(all_text),
                'word_count': len(all_text.split()) if all_text else 0,
                'title_complexity': len(title.split(',')) if title else 1,
                'has_summary': len(summary) > 0
            })

            # Status and process features
            status = bill.get('status', {})
            features.update({
                'status_type': status.get('statusType', ''),
                'committee': status.get('committeeName', ''),
                'has_committee': bool(status.get('committeeName')),
                'signed': bill.get('signed', False),
                'adopted': bill.get('adopted', False),
                'vetoed': bill.get('vetoed', False)
            })

            # Policy area classification (enhanced)
            title_lower = title.lower()

            # Multi-label policy classification
            policy_scores = {
                'trafficking_score': sum(1 for term in ['trafficking', 'victim', 'exploitation', 'prostitution'] if term in title_lower),
                'animal_score': sum(1 for term in ['animal', 'companion', 'pet', 'welfare'] if term in title_lower),
                'transport_score': sum(1 for term in ['license', 'driver', 'vehicle', 'motor', 'fee', 'transportation'] if term in title_lower),
                'criminal_score': sum(1 for term in ['crime', 'criminal', 'penalty', 'sentence', 'court'] if term in title_lower),
                'health_score': sum(1 for term in ['health', 'medical', 'insurance', 'care', 'treatment'] if term in title_lower),
                'education_score': sum(1 for term in ['education', 'school', 'student', 'teacher', 'university'] if term in title_lower),
                'fiscal_score': sum(1 for term in ['tax', 'revenue', 'budget', 'fiscal', 'finance'] if term in title_lower),
                'environment_score': sum(1 for term in ['environment', 'conservation', 'pollution', 'energy'] if term in title_lower),
                'senior_score': sum(1 for term in ['senior', 'elderly', 'aging', 'retirement'] if term in title_lower),
                'housing_score': sum(1 for term in ['housing', 'rent', 'tenant', 'landlord', 'property'] if term in title_lower),
                'emergency_score': sum(1 for term in ['emergency', 'disaster', 'response', 'safety'] if term in title_lower)
            }

            features.update(policy_scores)

            # Determine primary policy area
            max_score = max(policy_scores.values())
            if max_score > 0:
                primary_policy = [k.replace('_score', '') for k, v in policy_scores.items() if v == max_score][0]
            else:
                primary_policy = 'other'

            features['primary_policy'] = primary_policy

            # Text complexity features
            if all_text:
                # Simple readability metrics
                sentences = all_text.count('.') + all_text.count('!') + all_text.count('?')
                sentences = max(sentences, 1)  # Avoid division by zero

                features.update({
                    'avg_sentence_length': features['word_count'] / sentences,
                    'complexity_ratio': len([w for w in all_text.split() if len(w) > 6]) / features['word_count'] if features['word_count'] > 0 else 0,
                    'legislative_terms': sum(1 for term in ['shall', 'hereby', 'amend', 'section', 'subdivision'] if term in title_lower)
                })

            # Temporal features
            publish_date = bill.get('publishedDateTime', '')
            if publish_date and publish_date != '2009-01-01T00:00:01':  # Skip placeholder dates
                try:
                    if 'T' in publish_date:
                        date_obj = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    else:
                        date_obj = datetime.strptime(publish_date, '%Y-%m-%d')

                    features.update({
                        'publish_month': date_obj.month,
                        'publish_quarter': (date_obj.month - 1) // 3 + 1,
                        'publish_day_of_year': date_obj.timetuple().tm_yday,
                        'is_early_session': date_obj.month <= 4,  # Early in legislative session
                        'is_late_session': date_obj.month >= 10   # Late in legislative session
                    })
                except:
                    # Default values
                    features.update({
                        'publish_month': 1,
                        'publish_quarter': 1,
                        'publish_day_of_year': 1,
                        'is_early_session': True,
                        'is_late_session': False
                    })

            # Success and impact features
            success_score = 0
            if features['signed']:
                success_score = 3
            elif 'signed' in status.get('statusDesc', '').lower():
                success_score = 3
            elif status.get('statusType') in ['PASSED_SENATE', 'PASSED_ASSEMBLY']:
                success_score = 2
            elif 'floor' in status.get('statusDesc', '').lower():
                success_score = 1

            features['success_score'] = success_score
            features['high_impact'] = success_score >= 2

            # Bill number analysis (sometimes indicates priority)
            bill_num = bill.get('basePrintNo', '')
            if bill_num and bill_num.startswith('S'):
                try:
                    numeric_part = int(bill_num[1:])
                    features['bill_number_numeric'] = numeric_part
                    features['early_bill_number'] = numeric_part <= 1000  # Early in session
                    features['priority_bill'] = numeric_part <= 100      # Very early = priority?
                except:
                    features['bill_number_numeric'] = 0
                    features['early_bill_number'] = False
                    features['priority_bill'] = False
            else:
                features['bill_number_numeric'] = 0
                features['early_bill_number'] = False
                features['priority_bill'] = False

            clustering_data.append(features)

        except Exception as e:
            print(f"Error processing bill {bill_id}: {e}")

    df = pd.DataFrame(clustering_data)

    # Add derived features
    if not df.empty:
        # Session-relative features
        for session in df['session'].unique():
            session_bills = df[df['session'] == session]
            df.loc[df['session'] == session, 'session_productivity'] = len(session_bills)
            df.loc[df['session'] == session, 'session_avg_length'] = session_bills['word_count'].mean()

        # Policy diversity score
        policy_columns = [col for col in df.columns if col.endswith('_score')]
        df['policy_diversity'] = df[policy_columns].apply(lambda row: sum(1 for score in row if score > 0), axis=1)

        print(f"Created clustering dataset with {len(df)} bills and {len(df.columns)} features")

    return df

def perform_comprehensive_clustering(df):
    """Perform multiple clustering algorithms to find hidden patterns"""

    if df.empty or len(df) < 5:
        print("Insufficient data for clustering analysis")
        return {}

    print("=== COMPREHENSIVE CLUSTERING ANALYSIS ===")

    # Prepare feature matrices
    numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()

    # Remove ID columns from clustering
    clustering_features = [col for col in numerical_features
                          if col not in ['bill_number_numeric', 'session'] and not col.startswith('bill_')]

    if len(clustering_features) < 3:
        print("Insufficient numerical features for clustering")
        return {}

    X = df[clustering_features].fillna(0)

    print(f"Using {len(clustering_features)} features for clustering: {clustering_features[:10]}...")

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clustering_results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_info': {
            'n_bills': len(df),
            'n_features': len(clustering_features),
            'feature_names': clustering_features
        },
        'algorithms': {}
    }

    # 1. K-Means Clustering (different k values)
    print("Running K-Means clustering...")
    kmeans_results = {}

    for n_clusters in [3, 4, 5, 6, 8]:
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)

            # Calculate metrics
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            ch_score = calinski_harabasz_score(X_scaled, cluster_labels)
            db_score = davies_bouldin_score(X_scaled, cluster_labels)

            # Analyze clusters
            cluster_analysis = analyze_clusters(df, cluster_labels, clustering_features)

            kmeans_results[f'k_{n_clusters}'] = {
                'n_clusters': n_clusters,
                'silhouette_score': float(silhouette_avg),
                'calinski_harabasz_score': float(ch_score),
                'davies_bouldin_score': float(db_score),
                'cluster_analysis': cluster_analysis,
                'cluster_labels': cluster_labels.tolist()
            }

            print(f"  K={n_clusters}: Silhouette={silhouette_avg:.3f}, CH={ch_score:.1f}")

        except Exception as e:
            print(f"  K-Means with k={n_clusters} failed: {e}")

    clustering_results['algorithms']['kmeans'] = kmeans_results

    # 2. DBSCAN Clustering
    print("Running DBSCAN clustering...")
    try:
        # Try different eps values
        best_dbscan = None
        best_score = -1

        for eps in [0.5, 1.0, 1.5, 2.0, 2.5]:
            dbscan = DBSCAN(eps=eps, min_samples=3)
            cluster_labels = dbscan.fit_predict(X_scaled)

            n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)

            if n_clusters > 1 and n_clusters < len(df) / 2:  # Valid clustering
                try:
                    # Only calculate silhouette if we have valid clusters
                    if n_clusters > 1 and len(set(cluster_labels)) > 1:
                        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
                        if silhouette_avg > best_score:
                            best_score = silhouette_avg
                            best_dbscan = {
                                'eps': eps,
                                'n_clusters': n_clusters,
                                'n_noise': list(cluster_labels).count(-1),
                                'silhouette_score': float(silhouette_avg),
                                'cluster_labels': cluster_labels.tolist(),
                                'cluster_analysis': analyze_clusters(df, cluster_labels, clustering_features)
                            }
                except:
                    pass

        if best_dbscan:
            clustering_results['algorithms']['dbscan'] = best_dbscan
            print(f"  Best DBSCAN: eps={best_dbscan['eps']}, clusters={best_dbscan['n_clusters']}, noise={best_dbscan['n_noise']}")

    except Exception as e:
        print(f"  DBSCAN failed: {e}")

    # 3. Hierarchical Clustering
    print("Running Hierarchical clustering...")
    try:
        for n_clusters in [4, 5, 6]:
            agg = AgglomerativeClustering(n_clusters=n_clusters)
            cluster_labels = agg.fit_predict(X_scaled)

            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            cluster_analysis = analyze_clusters(df, cluster_labels, clustering_features)

            if 'hierarchical' not in clustering_results['algorithms']:
                clustering_results['algorithms']['hierarchical'] = {}

            clustering_results['algorithms']['hierarchical'][f'n_{n_clusters}'] = {
                'n_clusters': n_clusters,
                'silhouette_score': float(silhouette_avg),
                'cluster_labels': cluster_labels.tolist(),
                'cluster_analysis': cluster_analysis
            }

        print("  Hierarchical clustering completed")

    except Exception as e:
        print(f"  Hierarchical clustering failed: {e}")

    # 4. Gaussian Mixture Model
    print("Running Gaussian Mixture clustering...")
    try:
        best_gmm = None
        best_bic = float('inf')

        for n_components in [3, 4, 5, 6]:
            gmm = GaussianMixture(n_components=n_components, random_state=42)
            gmm.fit(X_scaled)
            cluster_labels = gmm.predict(X_scaled)

            bic = gmm.bic(X_scaled)
            aic = gmm.aic(X_scaled)

            if bic < best_bic:
                best_bic = bic
                best_gmm = {
                    'n_components': n_components,
                    'bic_score': float(bic),
                    'aic_score': float(aic),
                    'cluster_labels': cluster_labels.tolist(),
                    'cluster_analysis': analyze_clusters(df, cluster_labels, clustering_features)
                }

        if best_gmm:
            clustering_results['algorithms']['gaussian_mixture'] = best_gmm
            print(f"  Best GMM: components={best_gmm['n_components']}, BIC={best_gmm['bic_score']:.1f}")

    except Exception as e:
        print(f"  Gaussian Mixture failed: {e}")

    # 5. Anomaly Detection
    print("Running anomaly detection...")
    anomaly_results = {}

    try:
        # Isolation Forest
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        anomaly_labels = iso_forest.fit_predict(X_scaled)
        anomaly_bills = df[anomaly_labels == -1]

        anomaly_results['isolation_forest'] = {
            'n_anomalies': int(sum(anomaly_labels == -1)),
            'anomaly_indices': [int(i) for i, label in enumerate(anomaly_labels) if label == -1],
            'anomaly_bills': [{'bill_id': row['bill_id'], 'reason': 'Statistical outlier'} for _, row in anomaly_bills.iterrows()]
        }

        # Local Outlier Factor
        lof = LocalOutlierFactor(contamination=0.1)
        lof_labels = lof.fit_predict(X_scaled)
        lof_anomaly_bills = df[lof_labels == -1]

        anomaly_results['local_outlier_factor'] = {
            'n_anomalies': int(sum(lof_labels == -1)),
            'anomaly_indices': [int(i) for i, label in enumerate(lof_labels) if label == -1],
            'anomaly_bills': [{'bill_id': row['bill_id'], 'reason': 'Local outlier'} for _, row in lof_anomaly_bills.iterrows()]
        }

        clustering_results['anomaly_detection'] = anomaly_results
        print(f"  Anomaly detection: ISO={anomaly_results['isolation_forest']['n_anomalies']}, LOF={anomaly_results['local_outlier_factor']['n_anomalies']}")

    except Exception as e:
        print(f"  Anomaly detection failed: {e}")

    # 6. Dimensionality Reduction Analysis
    print("Running dimensionality reduction...")
    try:
        # PCA
        pca = PCA(n_components=min(10, X_scaled.shape[1]))
        X_pca = pca.fit_transform(X_scaled)

        # Explained variance
        explained_var = pca.explained_variance_ratio_
        cumulative_var = np.cumsum(explained_var)

        pca_results = {
            'explained_variance_ratio': explained_var.tolist(),
            'cumulative_variance': cumulative_var.tolist(),
            'n_components_90_percent': int(np.argmax(cumulative_var >= 0.9) + 1),
            'feature_importance': {}
        }

        # Feature importance in top components
        for i, component in enumerate(pca.components_[:3]):  # Top 3 components
            top_features = [(clustering_features[j], abs(component[j]))
                           for j in component.argsort()[-5:][::-1]]
            pca_results['feature_importance'][f'component_{i}'] = top_features

        clustering_results['dimensionality_reduction'] = {'pca': pca_results}
        print(f"  PCA: {pca_results['n_components_90_percent']} components explain 90% variance")

    except Exception as e:
        print(f"  Dimensionality reduction failed: {e}")

    return clustering_results

def analyze_clusters(df, cluster_labels, feature_names):
    """Analyze characteristics of each cluster"""

    cluster_analysis = {}
    unique_labels = set(cluster_labels)

    # Remove noise cluster if present
    if -1 in unique_labels:
        unique_labels.remove(-1)

    for cluster_id in unique_labels:
        cluster_mask = np.array(cluster_labels) == cluster_id
        cluster_data = df[cluster_mask]

        if len(cluster_data) == 0:
            continue

        # Basic statistics
        analysis = {
            'size': len(cluster_data),
            'percentage': float(len(cluster_data) / len(df) * 100),
            'bill_ids': cluster_data['bill_id'].tolist(),
            'years': cluster_data['year'].value_counts().to_dict(),
            'primary_policies': cluster_data['primary_policy'].value_counts().to_dict(),
            'committees': cluster_data['committee'].value_counts().to_dict() if 'committee' in cluster_data.columns else {},
            'success_rate': float(cluster_data['success_score'].mean()) if 'success_score' in cluster_data.columns else 0
        }

        # Feature characteristics
        numerical_features = cluster_data.select_dtypes(include=[np.number])
        feature_means = numerical_features.mean()

        # Find distinctive features (compared to overall mean)
        overall_means = df.select_dtypes(include=[np.number]).mean()
        distinctive_features = {}

        for feature in feature_names:
            if feature in feature_means and feature in overall_means:
                cluster_mean = feature_means[feature]
                overall_mean = overall_means[feature]
                if overall_mean != 0:
                    relative_diff = (cluster_mean - overall_mean) / overall_mean
                    if abs(relative_diff) > 0.2:  # 20% difference threshold
                        distinctive_features[feature] = {
                            'cluster_mean': float(cluster_mean),
                            'overall_mean': float(overall_mean),
                            'relative_difference': float(relative_diff)
                        }

        analysis['distinctive_features'] = distinctive_features

        # Cluster interpretation
        interpretation = interpret_cluster(analysis)
        analysis['interpretation'] = interpretation

        cluster_analysis[f'cluster_{cluster_id}'] = analysis

    return cluster_analysis

def interpret_cluster(cluster_analysis):
    """Provide human-readable interpretation of cluster characteristics"""

    size = cluster_analysis['size']
    policies = cluster_analysis.get('primary_policies', {})
    distinctive = cluster_analysis.get('distinctive_features', {})
    success_rate = cluster_analysis.get('success_rate', 0)

    interpretation = f"Cluster of {size} bills"

    # Add policy focus
    if policies:
        top_policy = max(policies, key=policies.get)
        if policies[top_policy] / size > 0.5:
            interpretation += f" focused on {top_policy.replace('_', ' ')}"

    # Add distinctive characteristics
    if distinctive:
        characteristics = []
        for feature, data in distinctive.items():
            if data['relative_difference'] > 0.3:
                characteristics.append(f"high {feature.replace('_', ' ')}")
            elif data['relative_difference'] < -0.3:
                characteristics.append(f"low {feature.replace('_', ' ')}")

        if characteristics:
            interpretation += f" with {', '.join(characteristics[:3])}"

    # Add success indicator
    if success_rate > 1:
        interpretation += " (high success rate)"
    elif success_rate == 0:
        interpretation += " (no legislative success)"

    return interpretation

def visualize_clusters(df, clustering_results):
    """Create visualizations for clustering results"""

    try:
        # Find best clustering result
        best_algorithm = None
        best_score = -1

        for algo, results in clustering_results.get('algorithms', {}).items():
            if algo == 'kmeans':
                for k, data in results.items():
                    if data['silhouette_score'] > best_score:
                        best_score = data['silhouette_score']
                        best_algorithm = ('kmeans', k, data)

        if not best_algorithm:
            print("No clustering results available for visualization")
            return

        algo_name, k_value, cluster_data = best_algorithm
        cluster_labels = cluster_data['cluster_labels']

        # Create visualization
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Lanza Bills Clustering Analysis ({algo_name.upper()}, {k_value})', fontsize=16, fontweight='bold')

        # 1. Cluster size distribution
        cluster_sizes = Counter(cluster_labels)
        axes[0,0].bar(cluster_sizes.keys(), cluster_sizes.values(), color='steelblue', alpha=0.7)
        axes[0,0].set_title('Cluster Size Distribution')
        axes[0,0].set_xlabel('Cluster ID')
        axes[0,0].set_ylabel('Number of Bills')

        # 2. Temporal distribution by cluster
        df_viz = df.copy()
        df_viz['cluster'] = cluster_labels

        for cluster_id in set(cluster_labels):
            cluster_data = df_viz[df_viz['cluster'] == cluster_id]
            year_counts = cluster_data.groupby('year').size()
            axes[0,1].plot(year_counts.index, year_counts.values,
                          marker='o', label=f'Cluster {cluster_id}', alpha=0.7)

        axes[0,1].set_title('Temporal Distribution by Cluster')
        axes[0,1].set_xlabel('Year')
        axes[0,1].set_ylabel('Number of Bills')
        axes[0,1].legend()

        # 3. Policy area distribution
        policy_cluster = pd.crosstab(df_viz['primary_policy'], df_viz['cluster'])
        policy_cluster.plot(kind='bar', stacked=True, ax=axes[1,0], alpha=0.8)
        axes[1,0].set_title('Policy Areas by Cluster')
        axes[1,0].set_xlabel('Policy Area')
        axes[1,0].set_ylabel('Number of Bills')
        axes[1,0].tick_params(axis='x', rotation=45)
        axes[1,0].legend(title='Cluster')

        # 4. Success rate by cluster
        success_by_cluster = df_viz.groupby('cluster')['success_score'].mean()
        axes[1,1].bar(success_by_cluster.index, success_by_cluster.values,
                     color='green', alpha=0.7)
        axes[1,1].set_title('Average Success Score by Cluster')
        axes[1,1].set_xlabel('Cluster ID')
        axes[1,1].set_ylabel('Average Success Score')

        plt.tight_layout()
        plt.savefig('lanza_clustering_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("📊 Clustering visualization saved as 'lanza_clustering_analysis.png'")

    except Exception as e:
        print(f"Visualization failed: {e}")

def main():
    """Main clustering analysis function"""

    print("=== LANZA CLUSTERING & PATTERN DISCOVERY ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Load data
    datasets = load_comprehensive_data()

    if not any(datasets.values()):
        print("❌ No data found. Please run previous analysis scripts first.")
        return

    # Create multi-dimensional dataset
    df = create_multi_dimensional_dataset(datasets)

    if df.empty:
        print("❌ No data available for clustering analysis.")
        return

    print(f"✅ Created multi-dimensional dataset with {len(df)} bills")
    print(f"✅ Features available: {len(df.columns)} total")
    print()

    # Perform comprehensive clustering
    clustering_results = perform_comprehensive_clustering(df)

    if not clustering_results:
        print("❌ Clustering analysis failed.")
        return

    # Create visualizations
    visualize_clusters(df, clustering_results)

    # Save results
    with open('clustering_analysis_results.json', 'w') as f:
        json.dump(clustering_results, f, indent=2, default=str)

    print("✅ Clustering analysis complete!")
    print(f"✅ Results saved to 'clustering_analysis_results.json'")

    # Display key insights
    print("\n=== CLUSTERING INSIGHTS ===")
    algorithms_used = list(clustering_results.get('algorithms', {}).keys())
    print(f"🤖 Algorithms used: {', '.join(algorithms_used)}")

    # Find and display best clustering
    best_silhouette = -1
    best_result = None

    for algo, results in clustering_results.get('algorithms', {}).items():
        if algo == 'kmeans':
            for k, data in results.items():
                if data['silhouette_score'] > best_silhouette:
                    best_silhouette = data['silhouette_score']
                    best_result = (algo, k, data)

    if best_result:
        algo_name, k_value, data = best_result
        print(f"🏆 Best clustering: {algo_name.upper()} with {data['n_clusters']} clusters")
        print(f"   Silhouette score: {data['silhouette_score']:.3f}")

        # Show cluster interpretations
        for cluster_id, analysis in data['cluster_analysis'].items():
            print(f"   • {cluster_id}: {analysis['interpretation']}")

    # Anomaly detection results
    if 'anomaly_detection' in clustering_results:
        anomalies = clustering_results['anomaly_detection']
        iso_anomalies = anomalies.get('isolation_forest', {}).get('n_anomalies', 0)
        lof_anomalies = anomalies.get('local_outlier_factor', {}).get('n_anomalies', 0)
        print(f"🚨 Anomalies detected: {iso_anomalies} (Isolation Forest), {lof_anomalies} (LOF)")

    return clustering_results, df

if __name__ == "__main__":
    main()