import re
import pandas as pd
from datetime import datetime

class WhatsAppChatParser:
    """Parser for WhatsApp chat exports with multiple date format support"""
    
    def __init__(self):
        # Common WhatsApp export patterns
        self.patterns = [
            r'^(\d{1,2}/\d{1,2}/\d{4}),\s(\d{1,2}:\d{2}\s(?:AM|PM))\s-\s([^:]+):\s(.+)$',
            r'^(\d{1,2}/\d{1,2}/\d{4}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)$',
            r'^(\d{1,2}/\d{1,2}/\d{2}),\s(\d{1,2}:\d{2}\s(?:AM|PM))\s-\s([^:]+):\s(.+)$',
            r'^(\d{1,2}/\d{1,2}/\d{2}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)$',
            r'^\[(\d{1,2}/\d{1,2}/\d{4}),\s(\d{1,2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)$',
            r'^(\d{1,2}\.\d{1,2}\.\d{2}),\s(\d{1,2}:\d{2})\s-\s([^:]+):\s(.+)$',
        ]
        
        self.date_formats = [
            '%d/%m/%Y',
            '%d/%m/%y', 
            '%m/%d/%Y',
            '%d.%m.%y'
        ]
        
        self.time_formats = [
            '%I:%M %p',  # 12-hour format with AM/PM
            '%H:%M',     # 24-hour format
            '%H:%M:%S'   # 24-hour format with seconds
        ]
    
    def parse_chat(self, text_content):
        """Parse chat content and return DataFrame"""
        lines = text_content.strip().split('\n')
        messages = []
        current_message = None
        
        parsed_count = 0
        unmatched_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Try to match against all patterns
            matched = False
            for pattern in self.patterns:
                match = re.match(pattern, line)
                if match:
                    # If we have a previous message, save it
                    if current_message:
                        messages.append(current_message)
                    
                    # Parse new message
                    date_str, time_str, user, message = match.groups()
                    
                    # Try to parse datetime
                    dt = self._parse_datetime(date_str, time_str)
                    if dt:
                        current_message = {
                            'datetime': dt,
                            'user': user.strip(),
                            'message': message.strip(),
                            'message_type': self._classify_message_type(message.strip())
                        }
                        parsed_count += 1
                        matched = True
                        break
            
            if not matched:
                # This might be a continuation of the previous message
                if current_message:
                    current_message['message'] += ' ' + line
                else:
                    unmatched_count += 1
                    if unmatched_count < 10:  # Only print first few unmatched lines
                        print(f"Unmatched line {line_num}: {line[:100]}...")
        
        # Don't forget the last message
        if current_message:
            messages.append(current_message)
        
        print(f"Parsing complete: {parsed_count} messages parsed, {unmatched_count} lines unmatched")
        
        if not messages:
            return None
        
        df = pd.DataFrame(messages)
        return df
    
    def _parse_datetime(self, date_str, time_str):
        """Parse date and time strings into datetime object"""
        for date_fmt in self.date_formats:
            for time_fmt in self.time_formats:
                try:
                    dt_str = f"{date_str} {time_str}"
                    dt_fmt = f"{date_fmt} {time_fmt}"
                    return datetime.strptime(dt_str, dt_fmt)
                except ValueError:
                    continue
        return None
    
    def _classify_message_type(self, message):
        """Classify message type based on content"""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['<media omitted>', 'image omitted', 'video omitted', 'audio omitted']):
            return 'media'
        elif any(keyword in message_lower for keyword in ['document omitted', 'contact card omitted']):
            return 'document'
        elif message_lower.startswith('http') or 'http' in message_lower:
            return 'link'
        elif any(keyword in message_lower for keyword in ['location:', 'live location']):
            return 'location'
        else:
            return 'text'
