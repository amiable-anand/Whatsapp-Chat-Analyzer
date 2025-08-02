import pandas as pd
from transformers import pipeline

class SentimentAnalyzer:
    """Sentiment analyzer using transformers"""
    
    def __init__(self):
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1
            )
        except Exception:
            # Fallback to default model
            self.sentiment_pipeline = pipeline("sentiment-analysis", device=-1)
    
    def analyze_sentiment(self, df):
        """Analyze sentiment of messages in the dataframe"""
        if df.empty:
            return {'overall_sentiment': {}, 'user_sentiment': {}, 'sentiment_timeline': pd.DataFrame()}
        
        # Filter text messages only
        text_messages = df[df['message_type'] == 'text'].copy()
        
        if text_messages.empty:
            return {'overall_sentiment': {}, 'user_sentiment': {}, 'sentiment_timeline': pd.DataFrame()}
        
        print(f"Analyzing sentiment for {len(text_messages)} text messages...")
        
        # Analyze sentiment in batches for performance
        batch_size = 100
        sentiments = []
        
        for i in range(0, len(text_messages), batch_size):
            batch = text_messages.iloc[i:i+batch_size]['message'].tolist()
            try:
                batch_results = self.sentiment_pipeline(batch)
                sentiments.extend(batch_results)
            except Exception as e:
                print(f"Error in sentiment analysis batch {i}: {e}")
                # Add neutral sentiment for failed batch
                sentiments.extend([{'label': 'NEUTRAL', 'score': 0.5}] * len(batch))
        
        # Add sentiment results to dataframe
        text_messages = text_messages.copy()
        text_messages['sentiment_label'] = [s['label'] for s in sentiments]
        text_messages['sentiment_score'] = [s['score'] for s in sentiments]
        
        # Normalize sentiment labels
        text_messages['sentiment_normalized'] = text_messages['sentiment_label'].apply(self._normalize_sentiment)
        
        # Calculate overall sentiment distribution
        overall_sentiment = text_messages['sentiment_normalized'].value_counts(normalize=True).to_dict()
        overall_sentiment = {k: round(v * 100, 1) for k, v in overall_sentiment.items()}
        
        # Calculate per-user sentiment
        user_sentiment = {}
        for user in text_messages['user'].unique():
            user_messages = text_messages[text_messages['user'] == user]
            user_dist = user_messages['sentiment_normalized'].value_counts(normalize=True).to_dict()
            user_sentiment[user] = {k: round(v * 100, 1) for k, v in user_dist.items()}
        
        # Create sentiment timeline (daily aggregation)
        text_messages['date'] = text_messages['datetime'].dt.date
        sentiment_timeline = text_messages.groupby(['date', 'sentiment_normalized']).size().unstack(fill_value=0)
        sentiment_timeline = sentiment_timeline.div(sentiment_timeline.sum(axis=1), axis=0) * 100
        sentiment_timeline = sentiment_timeline.round(1)
        
        return {
            'overall_sentiment': overall_sentiment,
            'user_sentiment': user_sentiment,
            'sentiment_timeline': sentiment_timeline,
            'detailed_data': text_messages[['datetime', 'user', 'message', 'sentiment_normalized', 'sentiment_score']]
        }
    
    def _normalize_sentiment(self, label):
        """Normalize different sentiment labels to standard format"""
        label_upper = label.upper()
        if label_upper in ['POSITIVE', 'POS', '1']:
            return 'positive'
        elif label_upper in ['NEGATIVE', 'NEG', '0']:
            return 'negative'
        else:
            return 'neutral'
    
    def get_sentiment_insights(self, sentiment_data):
        """Generate insights from sentiment analysis"""
        insights = []
        
        if not sentiment_data['overall_sentiment']:
            return ["No sentiment data available"]
        
        # Overall sentiment insights
        overall = sentiment_data['overall_sentiment']
        dominant_sentiment = max(overall, key=overall.get)
        insights.append(f"Overall conversation is {dominant_sentiment} ({overall[dominant_sentiment]:.1f}%)")
        
        # User sentiment insights
        if sentiment_data['user_sentiment']:
            most_positive_user = None
            most_negative_user = None
            max_positive = 0
            max_negative = 0
            
            for user, sentiments in sentiment_data['user_sentiment'].items():
                pos_score = sentiments.get('positive', 0)
                neg_score = sentiments.get('negative', 0)
                
                if pos_score > max_positive:
                    max_positive = pos_score
                    most_positive_user = user
                
                if neg_score > max_negative:
                    max_negative = neg_score
                    most_negative_user = user
            
            if most_positive_user:
                insights.append(f"Most positive user: {most_positive_user} ({max_positive:.1f}% positive)")
            
            if most_negative_user and max_negative > 20:  # Only mention if significantly negative
                insights.append(f"Most negative user: {most_negative_user} ({max_negative:.1f}% negative)")
        
        return insights
