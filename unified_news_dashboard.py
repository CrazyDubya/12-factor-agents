#!/usr/bin/env python3
"""
Unified News Intelligence Dashboard
One dashboard with everything: trends, clickable categories, actionable insights
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/data')
def get_all_data():
    """Get all dashboard data in one call"""
    return jsonify({
        'system': get_system_metrics(),
        'trends': get_trend_data(),
        'news': get_news_analysis(),
        'categories': get_categories(),
        'sources': get_source_analysis(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/category/<category_name>')
def get_category_details(category_name):
    """Get articles for a specific category with URLs"""
    try:
        with open('/Users/pup/news_reports/latest_news.txt', 'r') as f:
            lines = f.readlines()
        
        articles = []
        in_category = False
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for category header
            if line.startswith('🔸') and '(' in line:
                current_category = line.split('🔸')[1].split('(')[0].strip()
                in_category = (current_category.upper() == category_name.upper())
                i += 1
                # Skip the dashed line separator
                if i < len(lines) and lines[i].strip().startswith('--'):
                    i += 1
                continue
            
            # Parse article if in correct category
            if in_category and re.match(r'^\s*\d+\.', line):
                match = re.search(r'\[(.*?)\](.*)', line)
                if match:
                    source = match.group(1).strip()
                    headline = match.group(2).strip()
                    description = ""
                    url = ""
                    
                    # Look ahead for description and URL (they're indented)
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].rstrip()
                        
                        # Stop at next article, category, or section boundary
                        if (re.match(r'^\s*\d+\.', next_line) or 
                            next_line.startswith('🔸') or 
                            next_line.startswith('=')):
                            break
                        
                        # Skip empty lines but continue parsing
                        if next_line.strip() == "":
                            j += 1
                            continue
                            
                        # Check if line is indented (description or URL)
                        if next_line.startswith('    '):
                            stripped = next_line.strip()
                            if stripped.startswith('🔗'):
                                url = stripped.replace('🔗 ', '').strip()
                            elif stripped and not description:
                                description = stripped
                        
                        j += 1
                    
                    articles.append({
                        'source': source,
                        'headline': headline,
                        'description': description,
                        'url': url,
                        'full_line': line
                    })
            
            i += 1
        
        return jsonify({
            'category': category_name,
            'articles': articles[:20],  # Limit to 20 articles
            'total': len(articles)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def get_system_metrics():
    """Get system performance metrics"""
    try:
        # Master status
        with open('/Users/pup/data/master_status.json', 'r') as f:
            master_data = json.load(f)
        
        uptime_hours = master_data.get('uptime_seconds', 0) / 3600
        components = master_data.get('components', {})
        
        # Recent activity
        conn = sqlite3.connect('/Users/pup/data/scheduler_db.sqlite')
        cursor = conn.cursor()
        
        # Articles in last hour and today
        cursor.execute("SELECT SUM(article_count) FROM activity_log WHERE timestamp > datetime('now', '-1 hours')")
        articles_hour = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(article_count) FROM activity_log WHERE timestamp > datetime('now', '-24 hours')")
        articles_today = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM activity_log")
        total_scans = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'uptime_hours': round(uptime_hours, 1),
            'uptime_days': round(uptime_hours / 24, 1),
            'components_active': sum(1 for v in components.values() if v),
            'components_total': len(components),
            'articles_hour': articles_hour,
            'articles_today': articles_today,
            'total_scans': total_scans,
            'avg_per_hour': round(articles_today / 24, 1),
            'running': master_data.get('running', False)
        }
    except Exception as e:
        return {'error': str(e)}

def get_trend_data():
    """Get hourly and daily trends"""
    try:
        conn = sqlite3.connect('/Users/pup/data/scheduler_db.sqlite')
        cursor = conn.cursor()
        
        # Hourly patterns
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, 
                   COUNT(*) as scans, 
                   AVG(article_count) as avg_articles
            FROM activity_log 
            GROUP BY hour 
            ORDER BY hour
        ''')
        
        hourly_data = []
        for row in cursor.fetchall():
            hourly_data.append({
                'hour': int(row[0]),
                'scans': row[1],
                'avg_articles': round(row[2], 1)
            })
        
        # Daily patterns (last 7 days)
        cursor.execute('''
            SELECT date(timestamp) as day, 
                   COUNT(*) as scans,
                   SUM(article_count) as total_articles,
                   SUM(breaking_count) as total_breaking
            FROM activity_log 
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY day 
            ORDER BY day
        ''')
        
        daily_data = []
        for row in cursor.fetchall():
            daily_data.append({
                'date': row[0],
                'scans': row[1],
                'articles': row[2],
                'breaking': row[3]
            })
        
        # Mode analysis
        cursor.execute('''
            SELECT schedule_mode, COUNT(*) as count
            FROM activity_log 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY schedule_mode 
            ORDER BY count DESC
        ''')
        
        modes = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'hourly_patterns': hourly_data,
            'daily_patterns': daily_data,
            'mode_distribution': modes,
            'peak_hour': max(hourly_data, key=lambda x: x['avg_articles'])['hour'] if hourly_data else 0,
            'content_analysis': get_content_intelligence()
        }
    except Exception as e:
        return {'error': str(e)}

def get_content_intelligence():
    """Extract n-grams, entities, and trends from news content"""
    try:
        with open('/Users/pup/news_reports/latest_news.txt', 'r') as f:
            content = f.read()
        
        # Extract all headlines and descriptions
        text_content = []
        lines = content.split('\n')
        
        for line in lines:
            # Headlines with [Source] prefix
            if re.match(r'^\s*\d+\.\s*\[.*?\]', line):
                headline = re.sub(r'^\s*\d+\.\s*\[.*?\]\s*', '', line).strip()
                text_content.append(headline)
            # Description lines (indented, not URLs)
            elif line.startswith('    ') and not line.strip().startswith('🔗'):
                text_content.append(line.strip())
        
        # Combine all text
        combined_text = ' '.join(text_content).lower()
        
        # Initialize NLTK data if needed
        try:
            stop_words = set(stopwords.words('english'))
        except:
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'])
        
        # Tokenize and clean
        try:
            words = word_tokenize(combined_text)
        except:
            words = combined_text.split()
            
        clean_words = [word for word in words if word.isalpha() and len(word) > 2 and word not in stop_words]
        
        # Generate n-grams
        bigrams = list(ngrams(clean_words, 2))
        trigrams = list(ngrams(clean_words, 3))
        
        # Count frequencies
        word_freq = Counter(clean_words)
        bigram_freq = Counter([' '.join(bg) for bg in bigrams])
        trigram_freq = Counter([' '.join(tg) for tg in trigrams])
        
        # Extract entities (simple approach - capitalized words/phrases)
        entities = []
        for line in text_content:
            # Find capitalized words/phrases
            caps = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\b', line)
            entities.extend([cap for cap in caps if len(cap) > 2])
        
        entity_freq = Counter(entities)
        
        return {
            'top_words': dict(word_freq.most_common(15)),
            'top_bigrams': dict(bigram_freq.most_common(10)),
            'top_trigrams': dict(trigram_freq.most_common(8)),
            'entities': dict(entity_freq.most_common(12)),
            'total_text_analyzed': len(clean_words),
            'unique_words': len(set(clean_words))
        }
        
    except Exception as e:
        return {'error': f'Content analysis failed: {str(e)}'}

def get_news_analysis():
    """Get latest news report analysis"""
    try:
        with open('/Users/pup/news_reports/latest_news.txt', 'r') as f:
            content = f.read()
        
        # Extract total articles
        total_match = re.search(r'Total Articles: (\d+)', content)
        total_articles = int(total_match.group(1)) if total_match else 0
        
        # Extract sources
        sources = {}
        source_section = re.search(r'SOURCE BREAKDOWN:(.*?)====', content, re.DOTALL)
        if source_section:
            for line in source_section.group(1).split('\n'):
                if '•' in line and 'articles' in line:
                    parts = line.split('•')[1].strip().split(':')
                    if len(parts) == 2:
                        name = parts[0].strip()
                        count = int(re.search(r'(\d+)', parts[1]).group(1))
                        sources[name] = count
        
        # File age
        mtime = os.path.getmtime('/Users/pup/news_reports/latest_news.txt')
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        
        return {
            'total_articles': total_articles,
            'sources_active': len(sources),
            'sources': sources,
            'report_age_hours': round(age_hours, 1)
        }
    except Exception as e:
        return {'error': str(e)}

def get_categories():
    """Get news categories with counts"""
    try:
        with open('/Users/pup/news_reports/latest_news.txt', 'r') as f:
            content = f.read()
        
        categories = {}
        for line in content.split('\n'):
            if line.startswith('🔸') and '(' in line:
                category = line.split('🔸')[1].split('(')[0].strip()
                count_match = re.search(r'\((\d+) articles?\)', line)
                if count_match:
                    categories[category] = int(count_match.group(1))
        
        return categories
    except Exception as e:
        return {}

def get_source_analysis():
    """Analyze source performance"""
    try:
        health_file = '/Users/pup/cache/source_health.json'
        if os.path.exists(health_file):
            with open(health_file, 'r') as f:
                health_data = json.load(f)
            
            sources = []
            for name, data in health_data.items():
                sources.append({
                    'name': name,
                    'success_rate': round(data.get('success_rate', 0) * 100, 1),
                    'total_articles': data.get('total_articles', 0),
                    'last_success': data.get('last_success', ''),
                    'status': 'good' if data.get('success_rate', 0) > 0.8 else 'warning'
                })
            
            sources.sort(key=lambda x: x['success_rate'], reverse=True)
            return sources[:10]  # Top 10
        
        return []
    except Exception as e:
        return []

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>News Intelligence Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f0f23;
            color: #cccccc;
            line-height: 1.4;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            color: #00cc41;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header .status {
            color: #888;
            margin-top: 10px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
        }
        
        .card h3 {
            color: #00cc41;
            margin-bottom: 15px;
            font-size: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a2a;
        }
        
        .metric-row:last-child { border-bottom: none; }
        
        .metric-label { color: #aaa; }
        .metric-value { color: #fff; font-weight: 600; }
        .metric-value.good { color: #00cc41; }
        .metric-value.warning { color: #ffaa00; }
        .metric-value.danger { color: #ff4444; }
        
        .category-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #2a2a2a;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .category-item:hover {
            background: rgba(0, 204, 65, 0.1);
            border-radius: 4px;
            margin: 0 -5px;
            padding: 10px 5px;
        }
        
        .category-item:last-child { border-bottom: none; }
        
        .category-name {
            font-weight: 500;
            color: #fff;
        }
        
        .category-count {
            color: #00cc41;
            font-weight: bold;
        }
        
        .trend-chart {
            height: 200px;
            background: #2a2a2a;
            border-radius: 4px;
            margin: 15px 0;
            position: relative;
            padding: 10px;
        }
        
        .chart-bar {
            background: linear-gradient(180deg, #00cc41, #008830);
            border-radius: 2px;
            position: absolute;
            bottom: 10px;
            width: 15px;
            transition: all 0.3s ease;
        }
        
        .chart-bar:hover {
            background: linear-gradient(180deg, #00ff50, #00cc41);
        }
        
        .chart-label {
            position: absolute;
            bottom: -5px;
            font-size: 0.8rem;
            color: #888;
            transform: translateX(-50%);
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
        }
        
        .modal-content {
            background: #1e1e1e;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #333;
            border-radius: 8px;
            width: 80%;
            max-width: 800px;
            max-height: 80%;
            overflow-y: auto;
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover { color: #fff; }
        
        .article-item {
            padding: 10px 0;
            border-bottom: 1px solid #2a2a2a;
        }
        
        .article-source {
            color: #00cc41;
            font-weight: bold;
            font-size: 0.9rem;
        }
        
        .article-headline {
            color: #fff;
            margin-top: 4px;
        }
        
        .loading {
            text-align: center;
            color: #00cc41;
            padding: 40px;
        }
        
        .refresh-btn {
            background: #00cc41;
            color: #000;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .refresh-btn:hover {
            background: #00ff50;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 News Intelligence Dashboard</h1>
            <div class="status">
                <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
                <span id="last-update">Loading...</span>
            </div>
        </div>
        
        <div id="loading" class="loading">Loading intelligence data...</div>
        
        <div id="dashboard" style="display: none;">
            <div class="grid">
                <!-- System Status -->
                <div class="card">
                    <h3>🖥️ System Status</h3>
                    <div id="system-metrics"></div>
                </div>
                
                <!-- Activity Trends -->
                <div class="card">
                    <h3>📈 Hourly Activity Pattern</h3>
                    <div class="trend-chart" id="hourly-chart"></div>
                    <div id="trend-summary"></div>
                </div>
                
                <!-- Latest News -->
                <div class="card">
                    <h3>📰 Latest News Report</h3>
                    <div id="news-metrics"></div>
                </div>
                
                <!-- News Categories (Clickable) -->
                <div class="card">
                    <h3>📚 News Categories <small style="color: #888;">(click to view)</small></h3>
                    <div id="categories"></div>
                </div>
            </div>
            
            <div class="grid">
                <!-- Content Intelligence -->
                <div class="card">
                    <h3>🧠 Trending Topics (N-grams)</h3>
                    <div id="content-analysis"></div>
                </div>
                
                <!-- Key Entities -->
                <div class="card">
                    <h3>🏛️ Key Entities & People</h3>
                    <div id="entities-analysis"></div>
                </div>
                
                <!-- Source Performance -->
                <div class="card">
                    <h3>📡 Top News Sources</h3>
                    <div id="sources"></div>
                </div>
                
                <!-- Daily Trends -->
                <div class="card">
                    <h3>📅 7-Day Activity</h3>
                    <div id="daily-summary"></div>
                </div>
            </div>
        </div>
        
        <!-- Category Modal -->
        <div id="categoryModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h2 id="modal-title">Category Details</h2>
                <div id="modal-content"></div>
            </div>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                updateSystemMetrics(data.system);
                updateTrends(data.trends);
                updateNewsMetrics(data.news);
                updateCategories(data.categories);
                updateSources(data.sources);
                updateContentAnalysis(data.trends.content_analysis);
                
                document.getElementById('last-update').textContent = 'Last update: ' + new Date().toLocaleTimeString();
                document.getElementById('loading').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('loading').innerHTML = '<div style="color: #ff4444;">Error loading data: ' + error.message + '</div>';
            }
        }
        
        function updateSystemMetrics(system) {
            const healthClass = system.components_active === system.components_total ? 'good' : 'warning';
            document.getElementById('system-metrics').innerHTML = `
                <div class="metric-row">
                    <span class="metric-label">Status</span>
                    <span class="metric-value ${system.running ? 'good' : 'danger'}">${system.running ? '🟢 Running' : '🔴 Stopped'}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">${system.uptime_days}d (${system.uptime_hours}h)</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Components</span>
                    <span class="metric-value ${healthClass}">${system.components_active}/${system.components_total}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Articles Today</span>
                    <span class="metric-value">${system.articles_today}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Avg/Hour</span>
                    <span class="metric-value">${system.avg_per_hour}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Total Scans</span>
                    <span class="metric-value">${system.total_scans}</span>
                </div>
            `;
        }
        
        function updateTrends(trends) {
            if (trends.error) return;
            
            const chart = document.getElementById('hourly-chart');
            chart.innerHTML = '';
            
            const maxArticles = Math.max(...trends.hourly_patterns.map(h => h.avg_articles));
            const chartWidth = chart.offsetWidth - 20;
            const barWidth = Math.max(chartWidth / 24 - 2, 10);
            
            trends.hourly_patterns.forEach((hour, index) => {
                const height = (hour.avg_articles / maxArticles) * 180;
                const left = (index * (chartWidth / 24)) + 10;
                
                const bar = document.createElement('div');
                bar.className = 'chart-bar';
                bar.style.left = left + 'px';
                bar.style.width = barWidth + 'px';
                bar.style.height = height + 'px';
                bar.title = `${hour.hour}:00 - ${hour.avg_articles} avg articles (${hour.scans} scans)`;
                
                const label = document.createElement('div');
                label.className = 'chart-label';
                label.style.left = left + (barWidth/2) + 'px';
                label.textContent = hour.hour;
                
                chart.appendChild(bar);
                chart.appendChild(label);
            });
            
            document.getElementById('trend-summary').innerHTML = `
                <div class="metric-row">
                    <span class="metric-label">Peak Hour</span>
                    <span class="metric-value">${trends.peak_hour}:00</span>
                </div>
            `;
        }
        
        function updateNewsMetrics(news) {
            if (news.error) return;
            
            const ageClass = news.report_age_hours < 6 ? 'good' : news.report_age_hours < 12 ? 'warning' : 'danger';
            document.getElementById('news-metrics').innerHTML = `
                <div class="metric-row">
                    <span class="metric-label">Total Articles</span>
                    <span class="metric-value">${news.total_articles}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Active Sources</span>
                    <span class="metric-value">${news.sources_active}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Report Age</span>
                    <span class="metric-value ${ageClass}">${news.report_age_hours}h ago</span>
                </div>
            `;
        }
        
        function updateCategories(categories) {
            let html = '';
            Object.entries(categories).forEach(([category, count]) => {
                html += `
                    <div class="category-item" onclick="showCategory('${category}')">
                        <span class="category-name">${category}</span>
                        <span class="category-count">${count}</span>
                    </div>
                `;
            });
            document.getElementById('categories').innerHTML = html || '<div style="color: #666;">No categories available</div>';
        }
        
        function updateSources(sources) {
            if (!sources || sources.length === 0) {
                document.getElementById('sources').innerHTML = '<div style="color: #666;">No source data available</div>';
                return;
            }
            
            let html = '';
            sources.slice(0, 8).forEach(source => {
                const statusClass = source.status === 'good' ? 'good' : 'warning';
                html += `
                    <div class="metric-row">
                        <span class="metric-label">${source.name}</span>
                        <span class="metric-value ${statusClass}">${source.success_rate}% (${source.total_articles})</span>
                    </div>
                `;
            });
            document.getElementById('sources').innerHTML = html;
        }
        
        function updateContentAnalysis(analysis) {
            if (!analysis || analysis.error) {
                document.getElementById('content-analysis').innerHTML = `<div style="color: #f44336;">Analysis failed: ${analysis?.error || 'Unknown error'}</div>`;
                document.getElementById('entities-analysis').innerHTML = `<div style="color: #666;">Entities unavailable</div>`;
                return;
            }
            
            // Top topics and n-grams
            let contentHtml = `
                <div style="margin-bottom: 15px;">
                    <div class="metric-row">
                        <span class="metric-label">Words Analyzed</span>
                        <span class="metric-value">${analysis.total_text_analyzed}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Unique Words</span>
                        <span class="metric-value">${analysis.unique_words}</span>
                    </div>
                </div>
                <div style="margin-bottom: 10px; color: #64b5f6; font-weight: bold;">🔥 Top Bigrams:</div>
            `;
            
            Object.entries(analysis.top_bigrams || {}).slice(0, 6).forEach(([bigram, count]) => {
                contentHtml += `<div style="color: #ccc; font-size: 0.9rem; margin: 3px 0;">${bigram} (${count})</div>`;
            });
            
            contentHtml += '<div style="margin: 10px 0; color: #81c784; font-weight: bold;">⚡ Top Words:</div>';
            Object.entries(analysis.top_words || {}).slice(0, 8).forEach(([word, count]) => {
                contentHtml += `<span style="background: rgba(129, 199, 132, 0.2); padding: 3px 6px; margin: 2px; border-radius: 4px; font-size: 0.8rem; display: inline-block;">${word} (${count})</span>`;
            });
            
            document.getElementById('content-analysis').innerHTML = contentHtml;
            
            // Entities
            let entitiesHtml = '<div style="margin-bottom: 10px; color: #ff9800; font-weight: bold;">👥 People & Organizations:</div>';
            Object.entries(analysis.entities || {}).forEach(([entity, count]) => {
                entitiesHtml += `
                    <div class="metric-row" style="margin: 5px 0;">
                        <span class="metric-label" style="font-size: 0.9rem;">${entity}</span>
                        <span class="metric-value" style="background: rgba(255, 152, 0, 0.2); padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${count}</span>
                    </div>
                `;
            });
            
            document.getElementById('entities-analysis').innerHTML = entitiesHtml;
        }
        
        async function showCategory(categoryName) {
            try {
                const response = await fetch(`/api/category/${encodeURIComponent(categoryName)}`);
                const data = await response.json();
                
                document.getElementById('modal-title').textContent = `${categoryName} (${data.total} articles)`;
                
                let html = '';
                data.articles.forEach(article => {
                    const hasUrl = article.url && article.url.length > 0;
                    html += `
                        <div class="article-item" style="padding: 15px 0; border-bottom: 1px solid #333;">
                            <div class="article-source" style="color: #00cc41; font-weight: bold; font-size: 0.9rem;">[${article.source}]</div>
                            <div class="article-headline" style="color: #fff; margin: 5px 0; font-weight: bold;">
                                ${hasUrl ? `<a href="${article.url}" target="_blank" style="color: #64b5f6; text-decoration: none;">${article.headline}</a>` : article.headline}
                            </div>
                            ${article.description ? `<div style="color: #ccc; font-size: 0.9rem; margin-top: 5px;">${article.description}</div>` : ''}
                            ${hasUrl ? `<div style="margin-top: 8px;"><a href="${article.url}" target="_blank" style="color: #81c784; font-size: 0.8rem; text-decoration: none;">🔗 Read Full Article</a></div>` : ''}
                        </div>
                    `;
                });
                
                document.getElementById('modal-content').innerHTML = html || '<div style="color: #666; text-align: center; padding: 20px;">No articles found in this category</div>';
                document.getElementById('categoryModal').style.display = 'block';
                
            } catch (error) {
                alert('Error loading category details: ' + error.message);
            }
        }
        
        function closeModal() {
            document.getElementById('categoryModal').style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('categoryModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
        
        // Load data on page load and set up auto-refresh
        loadData();
        setInterval(loadData, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Starting UNIFIED News Intelligence Dashboard on http://localhost:8080")
    print("📊 One dashboard with everything: trends, clickable categories, real insights")
    app.run(host='0.0.0.0', port=8080, debug=False)