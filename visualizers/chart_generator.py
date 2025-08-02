import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

class ChartGenerator:
    """Generate interactive charts and visualizations"""

    def create_activity_timeline(self, df):
        """Create a line chart of messages over time"""
        df['date'] = df['datetime'].dt.date
        daily_counts = df['date'].value_counts().sort_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_counts.index, y=daily_counts.values, mode='lines+markers'))
        fig.update_layout(title='Daily Message Activity', xaxis_title='Date', yaxis_title='Message Count')
        return fig


    def create_sentiment_timeline(self, df, sentiment_data):
        """Create sentiment over time chart"""
        timeline = sentiment_data['sentiment_timeline']

        fig = px.area(timeline, facet_col=timeline.columns, facet_col_wrap=1,
                      labels={'value': 'Percentage (%)', 'date': 'Date'},
                      title='Sentiment Over Time')

        for i, label in enumerate(['positive', 'neutral', 'negative']):
            fig.data[i].name = label

        fig.update_layout(showlegend=True)
        return fig

    def create_hourly_heatmap(self, df):
        """Create a heatmap of hourly activity"""
        try:
            # Add date column and hour column
            df_copy = df.copy()
            df_copy['hour'] = df_copy['datetime'].dt.hour
            
            # Create hourly activity data for all 24 hours
            hourly_activity = df_copy.groupby('hour').size().reindex(range(24), fill_value=0)
            
            # Create bar chart for hourly activity
            fig = go.Figure(data=[
                go.Bar(
                    x=list(range(24)),
                    y=hourly_activity.values,
                    marker_color='rgba(55, 128, 191, 0.7)',
                    name='Messages'
                )
            ])
            
            # Update layout
            fig.update_layout(
                title='Hourly Activity Pattern',
                xaxis_title='Hour of Day',
                yaxis_title='Message Count',
                xaxis=dict(
                    tickmode='linear',
                    tick0=0,
                    dtick=1,
                    range=[-0.5, 23.5]
                ),
                showlegend=False
            )
            
            return fig
        except Exception as e:
            print(f"Error creating hourly heatmap: {e}")
            import traceback
            traceback.print_exc()
            # Return a simple empty figure with some sample data
            fig = go.Figure(data=[
                go.Bar(x=list(range(24)), y=[0]*24, name='No data')
            ])
            fig.update_layout(title='Hourly Activity Pattern - No Data Available')
            return fig

    def create_message_type_chart(self, df):
        """Create a pie chart of message types"""
        try:
            type_counts = df['message_type'].value_counts()
            
            if type_counts.empty:
                # Create empty chart with default data
                fig = go.Figure(data=[go.Pie(labels=['No Data'], values=[1])])
                fig.update_layout(title='Message Type Distribution - No Data')
                return fig
            
            # Create pie chart with proper formatting
            fig = go.Figure(data=[
                go.Pie(
                    labels=type_counts.index,
                    values=type_counts.values,
                    textinfo='label+percent',
                    hovertemplate='%{label}: %{value} messages<extra></extra>'
                )
            ])
            
            fig.update_layout(
                title='Message Type Distribution',
                showlegend=True
            )
            
            return fig
        except Exception as e:
            print(f"Error creating message type chart: {e}")
            # Return empty chart
            fig = go.Figure(data=[go.Pie(labels=['Error'], values=[1])])
            fig.update_layout(title='Message Type Distribution - Error')
            return fig

    def create_emoji_chart(self, emoji_data):
        """Create a bar chart for emoji usage"""
        emoji_df = pd.DataFrame(emoji_data['top_emojis'])

        fig = px.bar(emoji_df, x='emoji', y='count',
                     hover_data=['name', 'percentage'],
                     title='Top Emoji Usage',
                     labels={'count': 'Usage Count', 'emoji': 'Emoji'})
        return fig
    
    def create_sentiment_pie_chart(self, sentiment_distribution):
        """Create a pie chart for sentiment distribution"""
        labels = list(sentiment_distribution.keys())
        values = list(sentiment_distribution.values())
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title="Sentiment Distribution")
        return fig
    
    def create_user_activity_chart(self, df):
        """Create a bar chart of user activity"""
        user_counts = df['user'].value_counts()
        
        fig = go.Figure(data=[go.Bar(x=user_counts.index, y=user_counts.values)])
        fig.update_layout(title='User Activity', xaxis_title='User', yaxis_title='Message Count')
        return fig
    
    def create_timeline_chart(self, df):
        """Create a timeline chart of message activity"""
        df['date'] = df['datetime'].dt.date
        daily_counts = df.groupby('date').size()
        
        fig = go.Figure(data=[go.Scatter(x=daily_counts.index, y=daily_counts.values, mode='lines+markers')])
        fig.update_layout(title='Message Timeline', xaxis_title='Date', yaxis_title='Message Count')
        return fig

