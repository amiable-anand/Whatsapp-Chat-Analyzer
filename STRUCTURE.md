# WhatsInsight - Project Structure

```
WhatsInsight/
├── analyzers/
│   ├── emoji_analyzer.py      # Emoji detection and analysis
│   ├── keyword_analyzer.py    # Keyword extraction and trending words
│   ├── sentiment_analyzer.py  # Sentiment analysis using ML models
│   ├── toxicity_analyzer.py   # Toxicity detection
│   └── user_analyzer.py       # User activity and participation analysis
├── core/
│   └── chat_parser.py          # WhatsApp chat file parser
├── visualizers/
│   ├── chart_generator.py      # Interactive Plotly charts
│   └── wordcloud_generator.py  # Word cloud generation
├── templates/
│   ├── index.html              # Main upload page
│   ├── results.html            # Analysis results page
│   ├── 404.html                # Error page
│   └── 500.html                # Server error page
├── static/
│   ├── css/
│   │   └── styles.css          # Main styles
│   └── js/
│       └── results.js          # Frontend JavaScript
├── Captures/                   # Project screenshots
├── .github/                    # GitHub templates
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
├── Dockerfile                  # Docker container setup
├── Procfile                    # Heroku deployment
├── DEPLOYMENT.md               # Deployment instructions
├── .gitignore                  # Git ignore rules
└── .env.example                # Environment variables template
```

## Key Components

### Core Application
- **app.py**: Main Flask application with routes and logic
- **config.py**: Application configuration and settings

### Analysis Engine
- **analyzers/**: All analysis modules for different aspects
- **core/**: Chat parsing and data processing
- **visualizers/**: Chart and visualization generators

### Frontend
- **templates/**: HTML templates for the web interface
- **static/**: CSS and JavaScript assets
- **Captures/**: Screenshots and project images

### Deployment
- **Dockerfile**: Container setup
- **Procfile**: Heroku configuration
- **requirements.txt**: Python dependencies
- **DEPLOYMENT.md**: Deployment instructions

## Features

✅ **Sentiment Analysis** - Rule-based emotion detection
✅ **Emoji Analysis** - Comprehensive emoji statistics
✅ **User Activity** - Participation and engagement metrics
✅ **Interactive Charts** - Plotly visualizations
✅ **Word Clouds** - Visual text representation
✅ **Export Options** - JSON and CSV export
✅ **Responsive Design** - Mobile-friendly interface
✅ **Fast Processing** - Optimized for speed
✅ **Privacy-Focused** - Local processing only
