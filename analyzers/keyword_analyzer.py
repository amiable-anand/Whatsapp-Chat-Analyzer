import pandas as pd
import re
from collections import Counter

class KeywordAnalyzer:
    """Analyze keywords and trending words in chat"""
    
    def __init__(self):
        # Common stop words to filter out (English, Hindi, and Chat common words)
        self.stop_words = {
            # English stop words
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'not', 'no', 'yes', 'ok', 'okay',
            'im', 'ive', 'id', 'ill', 'its', 'dont', 'wont', 'cant', 'shouldnt', 'wouldnt', 'couldnt',
            'isnt', 'arent', 'wasnt', 'werent', 'hasnt', 'havent', 'hadnt', 'didnt', 'doesnt',
            # Hindi common words
            'hai', 'kya', 'aur', 'main', 'mein', 'hoon', 'hun', 'tum', 'aap', 'yeh', 'woh', 'jo',
            'ka', 'ki', 'ke', 'se', 'me', 'par', 'tha', 'thi', 'the', 'kar', 'kya', 'koi', 'bhi',
            'nahi', 'nahin', 'haan', 'han', 'agar', 'aise', 'waise', 'kaise', 'phir', 'ab', 'abhi',
            'bas', 'sirf', 'sab', 'kuch', 'kyun', 'kyunki', 'isliye', 'lekin', 'par', 'magar', 'nai',
            'jaisi', 'jaise', 'jitna', 'kitna', 'kaha', 'kahan', 'kab', 'kabhi', 'yaha', 'waha', 'mai' ,
            'iss', 'us', 'inn', 'unn', 'mere', 'mera', 'meri', 'tera', 'teri', 'unka', 'unki',
            # Chat/SMS common words
            'lol', 'haha', 'hehe', 'hmm', 'ohh', 'wow', 'cool', 'nice', 'good', 'bad', 'omg',
            'btw', 'brb', 'ttyl', 'thx', 'thanks', 'thank', 'welcome', 'plz', 'please', 'sorry',
            'bro', 'dude', 'yaar', 'yar', 'dost', 'bhai', 'behen', 'di', 'sir', 'mam', 'ji',
            # Common filler words
            'like', 'just', 'only', 'also', 'even', 'now', 'then', 'here', 'there', 'where',
            'when', 'what', 'who', 'how', 'why', 'which', 'whose', 'whom'
        }
    
    def analyze_keywords(self, df):
        """Analyze keywords and trending words"""
        if df.empty:
            return {
                'trending_words': [],
                'word_frequency': {},
                'user_vocabulary': {}
            }
        
        print("Analyzing keywords and trending words...")
        
        # Filter text messages
        text_messages = df[df['message_type'] == 'text']['message'].tolist()
        
        if not text_messages:
            return {
                'trending_words': [],
                'word_frequency': {},
                'user_vocabulary': {}
            }
        
        # Extract and count words
        all_words = []
        for message in text_messages:
            words = self._extract_words(message)
            all_words.extend(words)
        
        # Count word frequency
        word_counts = Counter(all_words)
        
        # Get trending words (most common excluding stop words)
        trending_words = [
            {'word': word, 'count': count, 'percentage': round((count / len(all_words)) * 100, 2)}
            for word, count in word_counts.most_common(50)
            if word.lower() not in self.stop_words and len(word) > 2
        ][:20]  # Top 20 trending words
        
        # User vocabulary analysis
        user_vocabulary = {}
        for user in df['user'].unique():
            user_messages = df[df['user'] == user]['message'].tolist()
            user_words = []
            for message in user_messages:
                if isinstance(message, str):
                    user_words.extend(self._extract_words(message))
            
            user_word_counts = Counter(user_words)
            user_vocabulary[user] = {
                'total_words': len(user_words),
                'unique_words': len(set(user_words)),
                'vocabulary_richness': round(len(set(user_words)) / len(user_words), 3) if user_words else 0,
                'top_words': [
                    {'word': word, 'count': count}
                    for word, count in user_word_counts.most_common(10)
                    if word.lower() not in self.stop_words and len(word) > 2
                ][:5]
            }
        
        return {
            'trending_words': trending_words,
            'word_frequency': dict(word_counts.most_common(100)),
            'user_vocabulary': user_vocabulary
        }
    
    def _extract_words(self, text):
        """Extract words from text, cleaning and filtering"""
        if not isinstance(text, str):
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words and filter
        words = [
            word.strip() for word in text.split()
            if len(word.strip()) > 2 and word.strip().isalpha()
        ]
        
        return words
    
    def get_keyword_insights(self, keyword_data):
        """Generate insights from keyword analysis"""
        insights = []
        
        if not keyword_data['trending_words']:
            insights.append("No significant trending words found")
            return insights
        
        # Most trending word
        top_word = keyword_data['trending_words'][0]
        insights.append(f"Most used word: '{top_word['word']}' ({top_word['count']} times)")
        
        # Vocabulary insights
        if keyword_data['user_vocabulary']:
            richest_vocab_user = max(
                keyword_data['user_vocabulary'].items(),
                key=lambda x: x[1]['vocabulary_richness']
            )
            insights.append(f"Richest vocabulary: {richest_vocab_user[0]} ({richest_vocab_user[1]['vocabulary_richness']:.2%} unique words)")
            
            most_talkative_user = max(
                keyword_data['user_vocabulary'].items(),
                key=lambda x: x[1]['total_words']
            )
            insights.append(f"Most words used: {most_talkative_user[0]} ({most_talkative_user[1]['total_words']} total words)")
        
        return insights
    
    def extract_keywords(self, text, top_n=10):
        """Extract keywords from text string - alias for compatibility"""
        if not text:
            return []
        
        words = self._extract_words(text)
        word_counts = Counter(words)
        
        return [
            {'word': word, 'count': count}
            for word, count in word_counts.most_common(top_n)
            if word.lower() not in self.stop_words and len(word) > 2
        ]
