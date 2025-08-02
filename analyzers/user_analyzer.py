import pandas as pd

class UserAnalyzer:
    """Analyze user participation and activity"""
    
    def analyze_users(self, df):
        """Analyze user participation and generate statistics"""
        if df.empty:
            return {'active_users_list': [], 'top_user': None, 'activity_timeline': pd.DataFrame()}
        
        # Count messages per user
        user_counts = df['user'].value_counts().reset_index()
        user_counts.columns = ['user', 'message_count']
        
        # Calculate percentages
        total_messages = len(df)
        user_counts['percentage'] = (user_counts['message_count'] / total_messages) * 100
        
        # Sort by message count and get top users
        user_counts = user_counts.sort_values(by='message_count', ascending=False).reset_index(drop=True)
        top_user = user_counts.iloc[0] if not user_counts.empty else None
        
        # Generate activity timeline (daily activity)
        df['date'] = df['datetime'].dt.date
        activity_timeline = df.groupby(['date', 'user']).size().unstack(fill_value=0)
        
        return {
            'active_users_list': user_counts.to_dict(orient='records'), 
            'top_user': top_user.to_dict() if top_user is not None else None, 
            'activity_timeline': activity_timeline.to_dict() if not activity_timeline.empty else {}
        }
    
    def get_user_stats(self, df):
        """Alias for analyze_users method to maintain compatibility"""
        return self.analyze_users(df)

