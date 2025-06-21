# SceneValidator

A tool for validating scene structure and continuity in scripts and media projects.

## Overview

SceneValidator analyzes script files and scene descriptions to identify potential continuity issues, logical inconsistencies, and structural problems. It uses the Gemini API to understand context and identify issues that might not be obvious through simple rule-based checking.

## Features

- Script structure validation
- Continuity checking across scenes
- Character consistency validation
- Timeline coherence analysis
- Setting and environment consistency checks
- Dialogue attribution verification

## Technical Implementation

- **Primary Technology:** Python + Gemini API
- **Trigger Mechanism:** File upload or API call
- **Input:** Script or scene files (supported formats: PDF, TXT, FDX, FOUNTAIN)
- **Output:** Validation report (JSON or HTML)

## Dependencies

- Python 3.8+
- Gemini API client
- Google Cloud Storage (optional, for file handling)
- Firebase (optional, for web interface)

## Installation

```bash
# Clone the repository
git clone https://github.com/dxaginfo/den-media-automation-tools.git

# Navigate to the tool directory
cd den-media-automation-tools/tools/SceneValidator

# Install dependencies
pip install -r requirements.txt

# Configure API access
cp config/config.example.json config/config.json
# Edit config.json with your API keys
```

## Usage

```python
from scene_validator import SceneValidator

# Initialize the validator
validator = SceneValidator(config_path='config/config.json')

# Validate a script file
result = validator.validate_file('path/to/script.fdx')

# Get the validation report
report = result.get_report(format='html')

# Save the report
with open('validation_report.html', 'w') as f:
    f.write(report)
```

## Integration with Other Tools

SceneValidator works well with:
- StoryboardGen: Use validation results to guide storyboard creation
- ContinuityTracker: Share continuity data between tools
- TimelineAssembler: Ensure timeline is consistent with script structure