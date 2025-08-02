import pandas as pd
import emoji
import re
from collections import Counter

class EmojiAnalyzer:
    """Analyze emoji usage patterns in chat messages"""
    
    def __init__(self):
        pass
    
    def analyze_emojis(self, df):
        """Analyze emoji usage in the dataframe"""
        if df.empty:
            return {
                'total_emojis': 0,
                'unique_emojis': 0,
                'top_emojis': [],
                'user_emoji_stats': {},
                'emoji_timeline': pd.DataFrame()
            }
        
        print("Analyzing emoji usage...")
        
        # Extract all emojis from messages
        all_emojis = []
        emoji_data = []
        
        for idx, row in df.iterrows():
            message = str(row['message'])
            message_emojis = self._extract_emojis(message)
            all_emojis.extend(message_emojis)
            
            # Store emoji data with metadata
            for emoji_char in message_emojis:
                emoji_data.append({
                    'datetime': row['datetime'],
                    'user': row['user'],
                    'emoji': emoji_char,
                    'emoji_name': self._get_emoji_name(emoji_char)
                })
        
        emoji_df = pd.DataFrame(emoji_data)
        
        # Calculate statistics
        total_emojis = len(all_emojis)
        unique_emojis = len(set(all_emojis))
        
        # Top emojis
        emoji_counts = Counter(all_emojis)
        top_emojis = [
            {
                'emoji': emoji_char,
                'name': self._get_emoji_name(emoji_char),
                'count': count,
                'percentage': round((count / total_emojis) * 100, 1) if total_emojis > 0 else 0
            }
            for emoji_char, count in emoji_counts.most_common(20)
        ]
        
        # Per-user emoji statistics
        user_emoji_stats = {}
        if not emoji_df.empty:
            for user in df['user'].unique():
                user_emojis = emoji_df[emoji_df['user'] == user]['emoji'].tolist()
                user_emoji_counts = Counter(user_emojis)
                
                user_emoji_stats[user] = {
                    'total_emojis': len(user_emojis),
                    'unique_emojis': len(set(user_emojis)),
                    'top_emojis': [
                        {
                            'emoji': emoji_char,
                            'name': self._get_emoji_name(emoji_char),
                            'count': count
                        }
                        for emoji_char, count in user_emoji_counts.most_common(5)
                    ]
                }
        
        # Emoji timeline (daily usage)
        emoji_timeline = pd.DataFrame()
        if not emoji_df.empty:
            emoji_df['date'] = emoji_df['datetime'].dt.date
            emoji_timeline = emoji_df.groupby('date').size().reset_index(name='emoji_count')
        
        return {
            'total_emojis': total_emojis,
            'unique_emojis': unique_emojis,
            'top_emojis': top_emojis,
            'user_emoji_stats': user_emoji_stats,
            'emoji_timeline': emoji_timeline,
            'emoji_diversity': round(unique_emojis / total_emojis, 3) if total_emojis > 0 else 0
        }
    
    def _extract_emojis(self, text):
        """Extract emojis from text"""
        if not text:
            return []
        
        # Use emoji library to extract emojis
        emojis = []
        for char in text:
            if char in emoji.EMOJI_DATA:
                emojis.append(char)
        
        return emojis
    
    def _get_emoji_name(self, emoji_char):
        """Get the name/description of an emoji"""
        try:
            return emoji.demojize(emoji_char).replace(':', '').replace('_', ' ').title()
        except:
            return "Unknown Emoji"
    
    def get_emoji_insights(self, emoji_data):
        """Generate insights from emoji analysis"""
        insights = []
        
        if emoji_data['total_emojis'] == 0:
            insights.append("No emojis used in this conversation")
            return insights
        
        # Overall emoji usage
        avg_emojis_per_msg = emoji_data['total_emojis'] / 100  # Approximate
        insights.append(f"Total emojis used: {emoji_data['total_emojis']} ({emoji_data['unique_emojis']} unique)")
        
        # Most popular emoji
        if emoji_data['top_emojis']:
            top_emoji = emoji_data['top_emojis'][0]
            insights.append(f"Most popular emoji: {top_emoji['emoji']} {top_emoji['name']} ({top_emoji['count']} times)")
        
        # Emoji diversity
        if emoji_data['emoji_diversity'] > 0.1:
            insights.append(f"High emoji diversity ({emoji_data['emoji_diversity']:.1%}) - varied emoji usage")
        elif emoji_data['emoji_diversity'] < 0.05:
            insights.append(f"Low emoji diversity ({emoji_data['emoji_diversity']:.1%}) - repetitive emoji usage")
        
        # User emoji habits
        if emoji_data['user_emoji_stats']:
            most_expressive_user = max(
                emoji_data['user_emoji_stats'].items(),
                key=lambda x: x[1]['total_emojis']
            )
            insights.append(f"Most expressive user: {most_expressive_user[0]} ({most_expressive_user[1]['total_emojis']} emojis)")
        
        return insights
