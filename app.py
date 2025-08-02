#!/usr/bin/env python3
"""
WhatsInsight - WhatsApp Chat Analyzer
A comprehensive WhatsApp chat analysis tool with sentiment analysis,
emoji detection, user activity tracking, and interactive visualizations.
"""

import os
import json
import traceback
import pandas as pd
import plotly.utils
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from datetime import datetime

from config import config
from core.chat_parser import WhatsAppChatParser
from analyzers.user_analyzer import UserAnalyzer
from analyzers.keyword_analyzer import KeywordAnalyzer
from analyzers.emoji_analyzer import EmojiAnalyzer
from visualizers.chart_generator import ChartGenerator
from visualizers.wordcloud_generator import WordCloudGenerator

app = Flask(__name__)
env_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env_name])

user_analyzer = UserAnalyzer()
keyword_analyzer = KeywordAnalyzer()
emoji_analyzer = EmojiAnalyzer()
chart_generator = ChartGenerator()
wordcloud_generator = WordCloudGenerator()

analysis_results = None
sentiment_analyzer = None
toxicity_analyzer = None

# Removed unused functions: allowed_file and extract_from_zip

def _analyze_sentiment_simple(text_messages):
    """Simple rule-based sentiment analysis"""
    if not text_messages:
        return {'positive': 33.3, 'negative': 33.3, 'neutral': 33.4}
    
    positive_words = {
        'good', 'great', 'awesome', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like',
        'happy', 'joy', 'pleased', 'excited', 'glad', 'perfect', 'best', 'beautiful', 'nice', 'cool',
        'thanks', 'thank', 'appreciate', 'grateful', 'wow', 'yay', 'haha', 'lol', 'congratulations',
        'congrats', 'well', 'super', 'brilliant', 'outstanding', 'magnificent', 'marvelous', 'terrific',
        'delighted', 'thrilled', 'ecstatic', 'cheerful', 'optimistic', 'positive', 'success', 'win',
        'victory', 'achieve', 'accomplished', 'proud', 'satisfying', 'blessed', 'lucky', 'fortunate'
    }
    
    negative_words = {
        'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry', 'mad', 'sad', 'upset',
        'disappointed', 'frustrated', 'annoyed', 'irritated', 'worried', 'concerned', 'stressed',
        'depressed', 'miserable', 'unhappy', 'sorry', 'apologize', 'mistake', 'error', 'wrong',
        'fail', 'failure', 'lost', 'lose', 'broken', 'damage', 'hurt', 'pain', 'sick', 'ill',
        'problem', 'issue', 'trouble', 'difficult', 'hard', 'challenging', 'struggle', 'tough',
        'worse', 'worst', 'disgusting', 'gross', 'yuck', 'boring', 'dull', 'stupid', 'dumb'
    }
    
    positive_count = 0
    negative_count = 0
    total_count = 0
    
    for message in text_messages:
        if isinstance(message, str):
            words = message.lower().split()
            total_count += 1
            
            pos_score = sum(1 for word in words if word in positive_words)
            neg_score = sum(1 for word in words if word in negative_words)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
    
    if total_count == 0:
        return {'positive': 33.3, 'negative': 33.3, 'neutral': 33.4}
    
    neutral_count = total_count - positive_count - negative_count
    
    return {
        'positive': round((positive_count / total_count) * 100, 1),
        'negative': round((negative_count / total_count) * 100, 1),
        'neutral': round((neutral_count / total_count) * 100, 1)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(url_for('index'))

        file = request.files['file']
        date_format = request.form.get('date_format', 'dd/mm/yyyy')

        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('index'))

        if file and file.filename.endswith('.txt'):
            # Read and process file
            file_content = file.read().decode('utf-8', errors='ignore')
            
            # Initialize analyzers
            parser = WhatsAppChatParser()
            
            # Skip heavy ML analyzers for faster processing
            global sentiment_analyzer, toxicity_analyzer
            print("Skipping ML analyzers for faster processing...")
            sentiment_analyzer = None
            toxicity_analyzer = None
            
            # Parse chat data
            try:
                df = parser.parse_chat(file_content)
                
                if df is None or df.empty:
                    flash('Unable to parse chat file. Please check the format.')
                    return redirect(url_for('index'))
                    
                # Ensure datetime column is properly formatted
                df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
                df = df.dropna(subset=['datetime'])  # Remove rows with invalid dates
                
                if df.empty:
                    flash('No valid messages found after parsing. Please check your chat file format.')
                    return redirect(url_for('index'))
                    
            except Exception as parse_error:
                print(f"Parsing error: {parse_error}")
                flash('Error parsing chat file. Please ensure it\'s a valid WhatsApp export.')
                return redirect(url_for('index'))
            
            # Basic statistics
            total_messages = len(df)
            unique_users = df['user'].nunique()
            date_range = f"{df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}"
            
            basic_stats = {
                'total_messages': total_messages,
                'unique_users': unique_users,
                'date_range': date_range,
                'avg_messages_per_day': round(total_messages / max((df['datetime'].max() - df['datetime'].min()).days, 1), 2)
            }
            
            # Text messages only for analysis
            text_messages = df[df['message_type'] == 'text']['message'].tolist()
            
            # Simple rule-based sentiment analysis
            print("Analyzing sentiment using rule-based approach...")
            sentiment_distribution = _analyze_sentiment_simple(text_messages)
            
            # Emoji analysis
            emoji_stats = emoji_analyzer.analyze_emojis(df)
            
            # User analysis
            user_stats = user_analyzer.get_user_stats(df)
            
            # Comprehensive keyword analysis
            keyword_analysis = keyword_analyzer.analyze_keywords(df)
            keyword_stats = keyword_analyzer.extract_keywords(' '.join(text_messages), top_n=10)
            
            # Toxicity analysis (optional, only if needed)
            toxicity_stats = {'toxic_messages': 0, 'toxicity_score': 0.0}
            if toxicity_analyzer is not None:
                try:
                    print("Analyzing toxicity...")
                    toxicity_stats = toxicity_analyzer.analyze_toxicity(df)
                except Exception as e:
                    print(f"Toxicity analysis failed: {e}")
                    toxicity_stats = {'toxic_messages': 0, 'toxicity_score': 0.0}
            
            # Generate word cloud
            wordcloud_img = None
            try:
                print("Generating word cloud...")
                wordcloud_img = wordcloud_generator.generate_wordcloud(df)
            except Exception as e:
                print(f"Word cloud generation failed: {e}")
            
            # Additional statistics
            total_words = sum(len(msg.split()) for msg in text_messages if isinstance(msg, str))
            media_count = len(df[df['message_type'] == 'media'])
            link_count = len(df[df['message_type'] == 'link'])
            
            # Enhanced basic stats
            basic_stats.update({
                'total_words': total_words,
                'media_messages': media_count,
                'link_messages': link_count,
                'avg_words_per_message': round(total_words / max(len(text_messages), 1), 1)
            })
            
            # Create comprehensive visualizations
            charts = {}
            
            try:
                print("Creating visualizations...")
                
                # Create sentiment pie chart
                sentiment_fig = chart_generator.create_sentiment_pie_chart(sentiment_distribution)
                charts['sentiment_chart'] = json.dumps(sentiment_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                # Create user activity chart
                user_activity_fig = chart_generator.create_user_activity_chart(df)
                charts['user_activity_chart'] = json.dumps(user_activity_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                # Create timeline chart
                timeline_fig = chart_generator.create_timeline_chart(df)
                charts['timeline_chart'] = json.dumps(timeline_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                # Create hourly activity heatmap
                heatmap_fig = chart_generator.create_hourly_heatmap(df)
                charts['heatmap_chart'] = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                # Create message type distribution chart
                message_type_fig = chart_generator.create_message_type_chart(df)
                charts['message_type_chart'] = json.dumps(message_type_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                # Create emoji usage chart if emojis exist
                if emoji_stats.get('total_emojis', 0) > 0:
                    emoji_fig = chart_generator.create_emoji_chart(emoji_stats)
                    charts['emoji_chart'] = json.dumps(emoji_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
                # Create activity timeline
                activity_timeline_fig = chart_generator.create_activity_timeline(df)
                charts['activity_timeline'] = json.dumps(activity_timeline_fig, cls=plotly.utils.PlotlyJSONEncoder)
                
            except Exception as e:
                print(f"Visualization error: {e}")
                traceback.print_exc()
            
            # Ensure all data is JSON serializable
            def make_serializable(obj):
                import datetime
                import numpy as np
                
                if isinstance(obj, pd.DataFrame):
                    return obj.to_dict('records')
                elif isinstance(obj, pd.Series):
                    return obj.to_dict()
                elif isinstance(obj, (datetime.date, datetime.datetime)):
                    return obj.isoformat()
                elif isinstance(obj, pd.Timestamp):
                    return obj.isoformat()
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {str(k): make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [make_serializable(item) for item in obj]
                elif hasattr(obj, 'isoformat'):  # Any date-like object
                    return obj.isoformat()
                elif hasattr(obj, 'item'):  # NumPy scalars
                    return obj.item()
                else:
                    return obj
            
            # Store results globally (ensure JSON serializable)
            global analysis_results
            analysis_results = {
                'basic_stats': make_serializable(basic_stats),
                'sentiment_distribution': make_serializable(sentiment_distribution),
                'emoji_stats': make_serializable(emoji_stats),
                'user_stats': make_serializable(user_stats),
                'keyword_stats': make_serializable(keyword_stats),
                'keyword_analysis': make_serializable(keyword_analysis),
                'toxicity_stats': make_serializable(toxicity_stats) if toxicity_stats else None,
                'wordcloud_img': wordcloud_img,
                'charts': charts,  # Already JSON strings
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return render_template('results.html', results=analysis_results)
            
        else:
            flash('Please upload a valid .txt file')
            return redirect(url_for('index'))
            
    except Exception as e:
        print(f"Analysis error: {e}")
        print(traceback.format_exc())
        flash(f'Error processing file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/stats')
def api_stats():
    """API endpoint for getting basic stats"""
    global analysis_results
    if analysis_results:
        return jsonify(analysis_results.get('basic_stats', {}))
    return jsonify({'error': 'No analysis data available'})

@app.route('/api/sentiment')
def api_sentiment():
    """API endpoint for sentiment data"""
    global analysis_results
    if analysis_results:
        return jsonify(analysis_results.get('sentiment_distribution', {}))
    return jsonify({'error': 'No sentiment data available'})

@app.route('/export/csv')
def export_csv():
    """Export analysis data as CSV"""
    global analysis_results
    if not analysis_results:
        return jsonify({'error': 'No analysis data available'}), 404
    
    # Create CSV content
    csv_content = "Type,Key,Value\n"
    
    # Basic stats
    for key, value in analysis_results.get('basic_stats', {}).items():
        csv_content += f"Basic Stats,{key},{value}\n"
    
    # Sentiment distribution
    for key, value in analysis_results.get('sentiment_distribution', {}).items():
        csv_content += f"Sentiment,{key},{value}\n"
    
    # Keywords
    for keyword in analysis_results.get('keyword_stats', []):
        csv_content += f"Keyword,{keyword.get('word', '')},{keyword.get('count', '')}\n"
    
    response = app.response_class(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=chat_analysis.csv'}
    )
    return response

@app.route('/export/json')
def export_json():
    """Export analysis data as JSON"""
    global analysis_results
    if not analysis_results:
        return jsonify({'error': 'No analysis data available'}), 404
    
    # Simple JSON export without complex serialization
    serializable_results = analysis_results
    
    response = app.response_class(
        json.dumps(serializable_results, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=chat_analysis.json'}
    )
    return response

@app.route('/health')
def health_check():
    """Health check endpoint for Azure"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Production WSGI configuration for deployment

if __name__ == '__main__':
    # Development server
    print("Starting WhatsInsight application...")
    port = int(os.environ.get('PORT', 5000))
    print(f"Server will run on http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop the server")
    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\nShutting down WhatsInsight...")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
