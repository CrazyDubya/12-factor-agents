import json
import pandas as pd
import numpy as np
import re
from datetime import datetime
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Core NLP and ML libraries
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF, TruncatedSVD
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import nltk

# Try to download NLTK data
try:
    import nltk.data
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        pass

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

import warnings
warnings.filterwarnings('ignore')

def load_bill_data():
    """Load comprehensive bill data with full text when available"""

    print("Loading bill data for NLP analysis...")

    all_bills = []
    bill_texts = {}

    # Load comprehensive involvement data
    try:
        with open('comprehensive_lanza_involvement.json', 'r') as f:
            involvement_data = json.load(f)
        all_bills.extend(involvement_data.get('all_bills_found', []))
    except FileNotFoundError:
        print("Warning: comprehensive_lanza_involvement.json not found")

    # Load individual bill files for full text
    bill_files = [
        'bill_S5914_2025.json',
        'bill_S7356_2025.json',
        'bill_S2589_2017.json',
        'bill_S5988A_2017.json',
        'bill_S8874_2017.json'
    ]

    for file_path in bill_files:
        try:
            with open(file_path, 'r') as f:
                bill_data = json.load(f)

            if bill_data.get('success'):
                bill = bill_data['result']
                bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"

                # Extract full text from amendments
                amendments = bill.get('amendments', {}).get('items', {})
                if amendments:
                    first_amendment = list(amendments.values())[0]
                    full_text = first_amendment.get('fullText', '')
                    memo = first_amendment.get('memo', '')

                    bill_texts[bill_id] = {
                        'full_text': full_text,
                        'memo': memo,
                        'law_section': first_amendment.get('lawSection', ''),
                        'law_code': first_amendment.get('lawCode', '')
                    }

                # Ensure bill is in all_bills
                if not any(b.get('basePrintNo') == bill.get('basePrintNo') and
                          b.get('session') == bill.get('session') for b in all_bills):
                    all_bills.append(bill)

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    print(f"Loaded {len(all_bills)} bills, {len(bill_texts)} with full text")
    return all_bills, bill_texts

def preprocess_text(text):
    """Advanced text preprocessing for NLP analysis"""

    if not text or not isinstance(text, str):
        return ""

    # Basic cleaning
    text = text.lower()
    text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove special characters

    # Tokenize and filter
    try:
        tokens = word_tokenize(text)

        # Remove stopwords
        try:
            stop_words = set(stopwords.words('english'))
            # Add legislative-specific stopwords
            stop_words.update(['bill', 'act', 'section', 'shall', 'law', 'state',
                             'new', 'york', 'senate', 'assembly', 'chapter',
                             'subdivision', 'paragraph', 'clause', 'thereof',
                             'hereby', 'amended', 'follows', 'effective', 'date'])
        except:
            stop_words = set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])

        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]

        # Lemmatization
        try:
            lemmatizer = WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(token) for token in tokens]
        except:
            pass

        return ' '.join(tokens)

    except:
        # Fallback to basic processing
        words = text.split()
        words = [word for word in words if len(word) > 2]
        return ' '.join(words)

def create_nlp_dataset(bills, bill_texts):
    """Create comprehensive dataset for NLP analysis"""

    nlp_data = []

    for bill in bills:
        if not isinstance(bill, dict):
            continue

        bill_id = f"{bill.get('basePrintNo', '')}-{bill.get('session', '')}"

        # Get text sources
        title = bill.get('title', '')
        summary = bill.get('summary', '')

        # Get full text if available
        full_text = ''
        memo = ''
        if bill_id in bill_texts:
            full_text = bill_texts[bill_id].get('full_text', '')
            memo = bill_texts[bill_id].get('memo', '')

        # Combine text sources
        all_text = f"{title} {summary} {memo}".strip()

        # Create comprehensive text corpus
        text_corpus = preprocess_text(all_text)

        if not text_corpus:
            continue

        # Extract features
        record = {
            'bill_id': bill_id,
            'bill_number': bill.get('basePrintNo', ''),
            'session': bill.get('session', 0),
            'title': title,
            'summary': summary,
            'text_corpus': text_corpus,
            'original_text': all_text,
            'title_length': len(title),
            'summary_length': len(summary),
            'total_text_length': len(all_text),
            'word_count': len(text_corpus.split()),
            'has_full_text': bill_id in bill_texts,
            'publish_year': bill.get('year', 0) or bill.get('session', 0)
        }

        # Status information
        status = bill.get('status', {})
        record.update({
            'status_type': status.get('statusType', ''),
            'committee': status.get('committeeName', ''),
            'signed': bill.get('signed', False),
            'adopted': bill.get('adopted', False)
        })

        # Legal classification
        if bill_id in bill_texts:
            record['law_section'] = bill_texts[bill_id].get('law_section', '')
            record['law_code'] = bill_texts[bill_id].get('law_code', '')

        nlp_data.append(record)

    return pd.DataFrame(nlp_data)

def perform_topic_modeling(df):
    """Advanced topic modeling using multiple algorithms"""

    print("=== TOPIC MODELING ANALYSIS ===")

    if df.empty or df['text_corpus'].str.len().sum() == 0:
        print("No text data available for topic modeling")
        return {}

    # Prepare text data
    documents = df['text_corpus'].fillna('').tolist()
    documents = [doc for doc in documents if len(doc.split()) >= 3]  # Filter very short documents

    if len(documents) < 5:
        print("Insufficient documents for topic modeling")
        return {}

    print(f"Analyzing {len(documents)} documents for topics...")

    topic_results = {
        'timestamp': datetime.now().isoformat(),
        'document_count': len(documents),
        'algorithms_used': []
    }

    # TF-IDF Vectorization
    print("Creating TF-IDF vectors...")
    tfidf = TfidfVectorizer(
        max_features=1000,
        min_df=2,
        max_df=0.8,
        ngram_range=(1, 3),
        stop_words='english'
    )

    try:
        tfidf_matrix = tfidf.fit_transform(documents)
        feature_names = tfidf.get_feature_names_out()

        print(f"TF-IDF matrix: {tfidf_matrix.shape}")

        # Get most important terms
        term_importance = np.array(tfidf_matrix.mean(axis=0)).flatten()
        top_terms_idx = term_importance.argsort()[-20:][::-1]
        top_terms = [(feature_names[i], term_importance[i]) for i in top_terms_idx]

        topic_results['top_terms'] = top_terms

    except Exception as e:
        print(f"TF-IDF failed: {e}")
        return topic_results

    # 1. Latent Dirichlet Allocation (LDA)
    print("Running LDA topic modeling...")
    try:
        n_topics = min(8, len(documents) // 3)  # Adjust based on document count

        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=100
        )

        lda_topics = lda.fit_transform(tfidf_matrix)

        # Extract topics
        lda_results = {
            'algorithm': 'LDA',
            'n_topics': n_topics,
            'topics': []
        }

        for topic_idx, topic in enumerate(lda.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topic_weights = topic[top_words_idx]

            lda_results['topics'].append({
                'topic_id': topic_idx,
                'top_words': top_words,
                'weights': topic_weights.tolist(),
                'interpretation': interpret_topic(top_words)
            })

        # Document-topic assignments
        doc_topic_assignments = []
        for doc_idx, doc_topics in enumerate(lda_topics):
            dominant_topic = doc_topics.argmax()
            doc_topic_assignments.append({
                'document_idx': doc_idx,
                'bill_id': df.iloc[doc_idx]['bill_id'] if doc_idx < len(df) else f"doc_{doc_idx}",
                'dominant_topic': int(dominant_topic),
                'topic_distribution': doc_topics.tolist()
            })

        lda_results['document_assignments'] = doc_topic_assignments
        topic_results['lda'] = lda_results
        topic_results['algorithms_used'].append('LDA')

        print(f"LDA completed: {n_topics} topics identified")

    except Exception as e:
        print(f"LDA failed: {e}")

    # 2. Non-Negative Matrix Factorization (NMF)
    print("Running NMF topic modeling...")
    try:
        n_topics = min(6, len(documents) // 3)

        nmf = NMF(n_components=n_topics, random_state=42, max_iter=200)
        nmf_topics = nmf.fit_transform(tfidf_matrix)

        nmf_results = {
            'algorithm': 'NMF',
            'n_topics': n_topics,
            'topics': []
        }

        for topic_idx, topic in enumerate(nmf.components_):
            top_words_idx = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            topic_weights = topic[top_words_idx]

            nmf_results['topics'].append({
                'topic_id': topic_idx,
                'top_words': top_words,
                'weights': topic_weights.tolist(),
                'interpretation': interpret_topic(top_words)
            })

        topic_results['nmf'] = nmf_results
        topic_results['algorithms_used'].append('NMF')

        print(f"NMF completed: {n_topics} topics identified")

    except Exception as e:
        print(f"NMF failed: {e}")

    # 3. Semantic Clustering
    print("Performing semantic clustering...")
    try:
        # Use SVD for dimensionality reduction
        svd = TruncatedSVD(n_components=50, random_state=42)
        doc_vectors = svd.fit_transform(tfidf_matrix)

        # K-means clustering
        n_clusters = min(8, len(documents) // 4)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(doc_vectors)

        # Analyze clusters
        clustering_results = {
            'algorithm': 'K-Means',
            'n_clusters': n_clusters,
            'clusters': []
        }

        for cluster_id in range(n_clusters):
            cluster_docs = [i for i, label in enumerate(cluster_labels) if label == cluster_id]

            if not cluster_docs:
                continue

            # Get representative terms for cluster
            cluster_tfidf = tfidf_matrix[cluster_docs].mean(axis=0)
            cluster_terms_idx = np.array(cluster_tfidf).flatten().argsort()[-10:][::-1]
            cluster_terms = [feature_names[i] for i in cluster_terms_idx]

            clustering_results['clusters'].append({
                'cluster_id': int(cluster_id),
                'document_count': len(cluster_docs),
                'representative_terms': cluster_terms,
                'bill_ids': [df.iloc[i]['bill_id'] if i < len(df) else f"doc_{i}" for i in cluster_docs],
                'interpretation': interpret_topic(cluster_terms)
            })

        topic_results['clustering'] = clustering_results
        topic_results['algorithms_used'].append('K-Means Clustering')

        print(f"Clustering completed: {n_clusters} clusters identified")

    except Exception as e:
        print(f"Clustering failed: {e}")

    return topic_results

def interpret_topic(top_words):
    """Interpret topic based on top words"""

    words = [word.lower() for word in top_words[:5]]

    # Define interpretation rules
    if any(word in words for word in ['trafficking', 'victim', 'exploitation', 'prostitution']):
        return "Human Trafficking & Victim Protection"
    elif any(word in words for word in ['animal', 'companion', 'pet', 'welfare']):
        return "Animal Welfare & Rights"
    elif any(word in words for word in ['license', 'driver', 'vehicle', 'motor', 'fee']):
        return "Transportation & Licensing"
    elif any(word in words for word in ['crime', 'criminal', 'penalty', 'sentence', 'court']):
        return "Criminal Justice & Public Safety"
    elif any(word in words for word in ['health', 'medical', 'insurance', 'care', 'treatment']):
        return "Healthcare & Medical Services"
    elif any(word in words for word in ['education', 'school', 'student', 'teacher', 'university']):
        return "Education & Academic Affairs"
    elif any(word in words for word in ['tax', 'revenue', 'budget', 'fiscal', 'finance']):
        return "Fiscal Policy & Taxation"
    elif any(word in words for word in ['environment', 'conservation', 'pollution', 'energy']):
        return "Environmental Protection"
    elif any(word in words for word in ['senior', 'elderly', 'aging', 'retirement']):
        return "Senior Citizens & Aging Services"
    elif any(word in words for word in ['housing', 'rent', 'tenant', 'landlord', 'property']):
        return "Housing & Real Estate"
    elif any(word in words for word in ['emergency', 'disaster', 'response', 'safety']):
        return "Emergency Management & Public Safety"
    else:
        return f"General Policy ({', '.join(words[:3])})"

def analyze_policy_evolution(df, topic_results):
    """Analyze how policy focus has evolved over time"""

    print("=== POLICY EVOLUTION ANALYSIS ===")

    evolution_analysis = {
        'timestamp': datetime.now().isoformat(),
        'time_periods': {},
        'policy_trends': {},
        'focus_shifts': []
    }

    if df.empty:
        return evolution_analysis

    # Group by time periods
    years = sorted(df['publish_year'].unique())

    for year in years:
        year_bills = df[df['publish_year'] == year]

        # Analyze policy focus for this year
        year_texts = ' '.join(year_bills['text_corpus'].fillna('').tolist())

        # Extract key terms
        try:
            tfidf = TfidfVectorizer(max_features=20, stop_words='english')
            year_tfidf = tfidf.fit_transform([year_texts])
            feature_names = tfidf.get_feature_names_out()
            term_scores = year_tfidf.toarray()[0]

            top_terms = [(feature_names[i], term_scores[i])
                        for i in term_scores.argsort()[-10:][::-1] if term_scores[i] > 0]

            evolution_analysis['time_periods'][str(year)] = {
                'bill_count': len(year_bills),
                'top_terms': top_terms,
                'policy_focus': interpret_topic([term[0] for term in top_terms[:5]]),
                'avg_text_length': year_bills['word_count'].mean()
            }

        except Exception as e:
            print(f"Failed to analyze year {year}: {e}")

    print(f"Analyzed policy evolution across {len(years)} years")

    return evolution_analysis

def sentiment_analysis(df):
    """Basic sentiment analysis of bill language"""

    print("=== SENTIMENT ANALYSIS ===")

    # Define positive and negative word lists (simplified)
    positive_words = {
        'protect', 'enhance', 'improve', 'benefit', 'support', 'help', 'assist',
        'strengthen', 'promote', 'advance', 'facilitate', 'enable', 'empower'
    }

    negative_words = {
        'prohibit', 'restrict', 'limit', 'prevent', 'stop', 'ban', 'forbid',
        'penalize', 'punish', 'fine', 'penalty', 'violation', 'offense'
    }

    sentiment_results = {
        'timestamp': datetime.now().isoformat(),
        'bill_sentiments': [],
        'overall_sentiment': {}
    }

    for _, row in df.iterrows():
        text = row['text_corpus'].lower().split()

        positive_score = sum(1 for word in text if word in positive_words)
        negative_score = sum(1 for word in text if word in negative_words)
        total_words = len(text)

        if total_words > 0:
            sentiment_score = (positive_score - negative_score) / total_words

            if sentiment_score > 0.01:
                sentiment_label = 'Positive'
            elif sentiment_score < -0.01:
                sentiment_label = 'Restrictive'
            else:
                sentiment_label = 'Neutral'
        else:
            sentiment_score = 0
            sentiment_label = 'Neutral'

        sentiment_results['bill_sentiments'].append({
            'bill_id': row['bill_id'],
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'positive_words': positive_score,
            'negative_words': negative_score
        })

    # Overall sentiment distribution
    sentiment_counts = Counter([s['sentiment_label'] for s in sentiment_results['bill_sentiments']])
    sentiment_results['overall_sentiment'] = {
        'distribution': dict(sentiment_counts),
        'avg_sentiment_score': np.mean([s['sentiment_score'] for s in sentiment_results['bill_sentiments']])
    }

    print(f"Sentiment analysis completed for {len(sentiment_results['bill_sentiments'])} bills")
    print(f"Sentiment distribution: {dict(sentiment_counts)}")

    return sentiment_results

def main():
    """Main NLP analysis function"""

    print("=== LANZA BILL NLP & POLICY CLASSIFIER ===")
    print(f"Timestamp: {datetime.now()}")
    print()

    # Load data
    bills, bill_texts = load_bill_data()

    if not bills:
        print("❌ No bill data found. Please run data harvesting first.")
        return

    # Create NLP dataset
    df = create_nlp_dataset(bills, bill_texts)

    if df.empty:
        print("❌ No processable text data found.")
        return

    print(f"✅ Created NLP dataset with {len(df)} bills")
    print(f"✅ {df['has_full_text'].sum()} bills have full text")
    print(f"✅ Average text length: {df['word_count'].mean():.1f} words")
    print()

    # Comprehensive NLP analysis
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_info': {
            'total_bills': len(df),
            'bills_with_full_text': int(df['has_full_text'].sum()),
            'avg_word_count': float(df['word_count'].mean()),
            'year_range': f"{df['publish_year'].min()}-{df['publish_year'].max()}"
        }
    }

    # 1. Topic Modeling
    topic_results = perform_topic_modeling(df)
    analysis_results['topic_modeling'] = topic_results

    # 2. Policy Evolution Analysis
    evolution_results = analyze_policy_evolution(df, topic_results)
    analysis_results['policy_evolution'] = evolution_results

    # 3. Sentiment Analysis
    sentiment_results = sentiment_analysis(df)
    analysis_results['sentiment_analysis'] = sentiment_results

    # 4. Statistical Analysis
    stats_analysis = {
        'word_count_stats': {
            'mean': float(df['word_count'].mean()),
            'median': float(df['word_count'].median()),
            'std': float(df['word_count'].std()),
            'min': int(df['word_count'].min()),
            'max': int(df['word_count'].max())
        },
        'bills_by_session': df['session'].value_counts().to_dict(),
        'bills_by_committee': df['committee'].value_counts().to_dict(),
        'success_indicators': {
            'signed_bills': int(df['signed'].sum()),
            'adopted_bills': int(df['adopted'].sum())
        }
    }
    analysis_results['statistical_analysis'] = stats_analysis

    # Save comprehensive results
    with open('nlp_policy_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)

    print("✅ NLP analysis complete!")
    print(f"✅ Results saved to 'nlp_policy_analysis.json'")

    # Display key insights
    print("\n=== KEY NLP INSIGHTS ===")
    print(f"📊 Analyzed {len(df)} bills with NLP techniques")

    if 'algorithms_used' in topic_results:
        print(f"🤖 Topic modeling algorithms: {', '.join(topic_results['algorithms_used'])}")

    if 'lda' in topic_results:
        print(f"📈 LDA identified {topic_results['lda']['n_topics']} main policy topics")
        for topic in topic_results['lda']['topics'][:3]:
            print(f"   • {topic['interpretation']}: {', '.join(topic['top_words'][:5])}")

    if sentiment_results['overall_sentiment']:
        sentiment_dist = sentiment_results['overall_sentiment']['distribution']
        print(f"💭 Sentiment distribution: {sentiment_dist}")

    return analysis_results, df

if __name__ == "__main__":
    main()