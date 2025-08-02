import pandas as pd
import base64
import io
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import re

class WordCloudGenerator:
    """Generate word clouds from chat messages"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'not', 'no', 'yes', 'ok', 'okay',
            'im', 'ive', 'id', 'ill', 'its', 'dont', 'wont', 'cant', 'shouldnt', 'wouldnt', 'couldnt',
            'isnt', 'arent', 'wasnt', 'werent', 'hasnt', 'havent', 'hadnt', 'didnt', 'doesnt', 'media',
            'omitted', 'image', 'video', 'audio', 'document', 'contact', 'card', 'location'
        }
    
    def generate_wordcloud(self, input_data):
        """Generate word cloud from chat messages"""
        # Handle both DataFrame and string inputs
        if isinstance(input_data, str):
            all_text = input_data
        elif hasattr(input_data, 'empty') and input_data.empty:
            return None
        else:
            # Assume it's a DataFrame
            text_messages = input_data[input_data['message_type'] == 'text']['message'].tolist()
            
            if not text_messages:
                return None
                
            # Combine all messages into one text
            all_text = ' '.join([str(msg) for msg in text_messages if str(msg).strip()])
        
        # Clean text
        all_text = self._clean_text(all_text)
        
        if not all_text.strip():
            return None
        
        try:
            # Create word cloud
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                stopwords=self.stop_words,
                max_words=100,
                colormap='viridis',
                relative_scaling=0.5,
                min_font_size=10
            ).generate(all_text)
            
            # Convert to image
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            
            # Save to base64 string
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            
            img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
            plt.close()
            
            return img_base64
            
        except Exception as e:
            print(f"Error generating word cloud: {e}")
            return None
    
    def _clean_text(self, text):
        """Clean text for word cloud generation"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
