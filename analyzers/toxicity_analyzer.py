import pandas as pd
from transformers import pipeline
import re

class ToxicityAnalyzer:
    """Analyze toxicity and harmful content in messages"""
    
    def __init__(self):
        try:
            self.toxicity_pipeline = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=-1
            )
        except Exception:
            self.toxicity_pipeline = None
            self._init_rule_based_detector()
    
    def _init_rule_based_detector(self):
        """Initialize rule-based toxicity detection as fallback"""
        self.toxic_patterns = [
            r'\b(hate|stupid|idiot|dumb|moron)\b',
            r'\b(shut up|shutup)\b',
            r'\b(kill yourself|kys)\b',
            r'\b(go die|die)\b',
            # Add more patterns as needed, but be careful not to be too aggressive
        ]
    
    def analyze_toxicity(self, df):
        """Analyze toxicity in messages"""
        if df.empty:
            return {
                'toxic_messages': 0,
                'toxicity_score': 0.0,
                'user_toxicity': {},
                'toxic_examples': []
            }
        
        print("Analyzing message toxicity...")
        
        # Filter text messages only
        text_messages = df[df['message_type'] == 'text'].copy()
        
        if text_messages.empty:
            return {
                'toxic_messages': 0,
                'toxicity_score': 0.0,
                'user_toxicity': {},
                'toxic_examples': []
            }
        
        toxic_count = 0
        toxic_examples = []
        user_toxicity = {}
        
        # Initialize user toxicity counters
        for user in df['user'].unique():
            user_toxicity[user] = {'toxic_count': 0, 'total_messages': 0}
        
        # Analyze each message
        for idx, row in text_messages.iterrows():
            message = str(row['message'])
            user = row['user']
            
            user_toxicity[user]['total_messages'] += 1
            
            is_toxic = self._is_toxic(message)
            
            if is_toxic:
                toxic_count += 1
                user_toxicity[user]['toxic_count'] += 1
                
                # Store example (truncated for privacy)
                if len(toxic_examples) < 5:  # Limit examples
                    toxic_examples.append({
                        'user': user,
                        'message': message[:100] + '...' if len(message) > 100 else message,
                        'datetime': row['datetime'].strftime('%Y-%m-%d %H:%M')
                    })
        
        # Calculate toxicity percentages for users
        for user in user_toxicity:
            total = user_toxicity[user]['total_messages']
            toxic = user_toxicity[user]['toxic_count']
            user_toxicity[user]['toxicity_percentage'] = round((toxic / total) * 100, 1) if total > 0 else 0
        
        # Overall toxicity score
        total_messages = len(text_messages)
        toxicity_score = round((toxic_count / total_messages) * 100, 1) if total_messages > 0 else 0
        
        return {
            'toxic_messages': toxic_count,
            'toxicity_score': toxicity_score,
            'user_toxicity': user_toxicity,
            'toxic_examples': toxic_examples
        }
    
    def _is_toxic(self, message):
        """Determine if a message is toxic"""
        if not message or len(message.strip()) < 3:
            return False
        
        if self.toxicity_pipeline:
            try:
                # Use ML model
                result = self.toxicity_pipeline(message)
                # Check if the model returns toxicity labels
                if isinstance(result, list) and len(result) > 0:
                    label = result[0].get('label', '').upper()
                    score = result[0].get('score', 0)
                    return 'TOXIC' in label and score > 0.7
            except Exception as e:
                print(f"Error in ML toxicity detection: {e}")
                # Fall back to rule-based
                pass
        
        # Rule-based detection
        message_lower = message.lower()
        for pattern in self.toxic_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        
        return False
    
    def get_toxicity_insights(self, toxicity_data):
        """Generate insights from toxicity analysis"""
        insights = []
        
        if toxicity_data['toxic_messages'] == 0:
            insights.append("✅ No toxic content detected - this is a healthy conversation!")
            return insights
        
        # Overall toxicity
        insights.append(f"⚠️ {toxicity_data['toxic_messages']} potentially toxic messages detected ({toxicity_data['toxicity_score']}% of total)")
        
        # User toxicity
        if toxicity_data['user_toxicity']:
            most_toxic_user = max(
                toxicity_data['user_toxicity'].items(),
                key=lambda x: x[1]['toxicity_percentage']
            )
            
            if most_toxic_user[1]['toxicity_percentage'] > 10:
                insights.append(f"Most toxic user: {most_toxic_user[0]} ({most_toxic_user[1]['toxicity_percentage']}% toxic messages)")
        
        # Recommendations
        if toxicity_data['toxicity_score'] > 10:
            insights.append("💡 Consider moderating this conversation or addressing toxic behavior")
        elif toxicity_data['toxicity_score'] > 5:
            insights.append("💡 Some concerning messages detected - monitor for escalation")
        
        return insights
