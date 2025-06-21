# StoryboardGen

A tool for generating storyboards from script text using the Gemini API.

## Overview

StoryboardGen analyzes script content to automatically generate storyboard images and layouts. It uses natural language understanding to identify key visual elements and scene composition, then creates appropriate storyboard frames to help visualize the script.

## Features

- Automatic scene breakdown
- AI-powered image generation
- Scene composition analysis
- Character positioning suggestions
- Camera angle and framing recommendations
- Export to various formats (PNG, PDF, HTML)
- Integration with other production tools

## Technical Implementation

- **Primary Technology:** Python + Gemini API
- **Trigger Mechanism:** File upload or API call
- **Input:** Script files (supported formats: PDF, TXT, FDX, FOUNTAIN)
- **Output:** Storyboard images or document (PNG, PDF, HTML)

## Dependencies

- Python 3.8+
- Gemini API client
- Google Cloud Storage
- Pillow (Python Imaging Library)
- ReportLab (for PDF generation)
- Flask (for web interface)

## Installation

```bash
# Clone the repository
git clone https://github.com/dxaginfo/den-media-automation-tools.git

# Navigate to the tool directory
cd den-media-automation-tools/tools/StoryboardGen

# Install dependencies
pip install -r requirements.txt

# Configure API access
cp config/config.example.json config/config.json
# Edit config.json with your API keys
```

## Usage

```python
from storyboard_gen import StoryboardGenerator

# Initialize the generator
generator = StoryboardGenerator(config_path='config/config.json')

# Generate storyboard from script file
storyboard = generator.generate_from_script('path/to/script.fdx')

# Export the storyboard to PDF
storyboard.export_pdf('storyboard_output.pdf')

# Export individual frames
storyboard.export_frames('output_directory')
```

## Integration with Other Tools

StoryboardGen works well with:
- SceneValidator: Use validated script data to ensure accurate storyboards
- TimelineAssembler: Import storyboard frames into the timeline
- EnvironmentTagger: Use environmental data to enhance storyboard generation