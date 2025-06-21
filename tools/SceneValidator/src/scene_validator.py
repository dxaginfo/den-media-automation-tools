#!/usr/bin/env python3
"""
SceneValidator: A tool for validating scene structure and continuity in scripts.
Uses Gemini API to analyze script content and identify potential issues.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SceneValidator')

# Import optional dependencies (wrapped to avoid errors if not installed)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("Gemini API not available. Install with: pip install google-generativeai")
    GEMINI_AVAILABLE = False

@dataclass
class ValidationIssue:
    """Represents an issue found during validation."""
    issue_type: str
    description: str
    location: str
    severity: str  # 'high', 'medium', 'low'
    suggestions: List[str]

@dataclass
class ValidationResult:
    """Contains the results of a validation operation."""
    valid: bool
    issues: List[ValidationIssue]
    summary: str
    
    def get_report(self, format: str = 'json') -> str:
        """Generate a formatted report of validation results."""
        if format.lower() == 'json':
            return json.dumps({
                'valid': self.valid,
                'issues': [vars(issue) for issue in self.issues],
                'summary': self.summary
            }, indent=2)
        elif format.lower() == 'html':
            # Simple HTML report
            html = "<html><head><title>Scene Validation Report</title>"
            html += "<style>body{font-family:Arial;max-width:800px;margin:0 auto;padding:20px}"
            html += ".valid{color:green}.invalid{color:red}"
            html += ".high{color:red}.medium{color:orange}.low{color:blue}"
            html += "table{width:100%;border-collapse:collapse}"
            html += "td,th{border:1px solid #ddd;padding:8px}</style></head><body>"
            html += f"<h1>Scene Validation Report</h1>"
            html += f"<h2 class=\"{'valid' if self.valid else 'invalid'}\">Status: {'Valid' if self.valid else 'Invalid'}</h2>"
            html += f"<h3>Summary</h3><p>{self.summary}</p>"
            
            if self.issues:
                html += "<h3>Issues</h3><table>"
                html += "<tr><th>Type</th><th>Description</th><th>Location</th><th>Severity</th><th>Suggestions</th></tr>"
                for issue in self.issues:
                    html += f"<tr>"
                    html += f"<td>{issue.issue_type}</td>"
                    html += f"<td>{issue.description}</td>"
                    html += f"<td>{issue.location}</td>"
                    html += f"<td class=\"{issue.severity}\">{issue.severity.capitalize()}</td>"
                    html += f"<td><ul>{''.join([f'<li>{s}</li>' for s in issue.suggestions])}</ul></td>"
                    html += "</tr>"
                html += "</table>"
            else:
                html += "<p>No issues found!</p>"
                
            html += "</body></html>"
            return html
        else:
            raise ValueError(f"Unsupported report format: {format}")


class SceneValidator:
    """
    A validator for scene structure and continuity in scripts.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the validator with optional configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                
        # Initialize Gemini API if available and configured
        self.gemini_model = None
        if GEMINI_AVAILABLE and 'gemini_api_key' in self.config:
            genai.configure(api_key=self.config['gemini_api_key'])
            model_name = self.config.get('gemini_model', 'gemini-pro')
            self.gemini_model = genai.GenerativeModel(model_name)
            logger.info(f"Initialized Gemini model: {model_name}")
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate a script file for issues.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            ValidationResult object with validation details
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Script file not found: {file_path}")
        
        # Read the file content
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Determine file type from extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Validate based on content and file type
        return self.validate_content(content, file_type=file_ext)
    
    def validate_content(self, content: str, file_type: str = '.txt') -> ValidationResult:
        """
        Validate script content directly.
        
        Args:
            content: The script content to validate
            file_type: The type of file (extension)
            
        Returns:
            ValidationResult object with validation details
        """
        issues = []
        
        # Basic validation rules (these would be expanded in a real implementation)
        if not content:
            issues.append(ValidationIssue(
                issue_type="empty_content",
                description="The script content is empty",
                location="entire file",
                severity="high",
                suggestions=["Add content to the script file"]
            ))
            return ValidationResult(
                valid=False,
                issues=issues,
                summary="Validation failed: Empty script content"
            )
        
        # Scene structure validation
        scene_issues = self._validate_scene_structure(content, file_type)
        issues.extend(scene_issues)
        
        # Continuity validation
        continuity_issues = self._validate_continuity(content)
        issues.extend(continuity_issues)
        
        # Character consistency validation
        character_issues = self._validate_character_consistency(content)
        issues.extend(character_issues)
        
        # Use Gemini for advanced analysis if available
        if self.gemini_model:
            gemini_issues = self._analyze_with_gemini(content)
            issues.extend(gemini_issues)
        
        # Determine overall validity
        valid = len([i for i in issues if i.severity == 'high']) == 0
        
        # Generate summary
        if not issues:
            summary = "No issues found in the script."
        else:
            high_count = len([i for i in issues if i.severity == 'high'])
            medium_count = len([i for i in issues if i.severity == 'medium'])
            low_count = len([i for i in issues if i.severity == 'low'])
            summary = f"Found {len(issues)} issues: {high_count} high, {medium_count} medium, {low_count} low severity."
        
        return ValidationResult(
            valid=valid,
            issues=issues,
            summary=summary
        )
    
    def _validate_scene_structure(self, content: str, file_type: str) -> List[ValidationIssue]:
        """
        Validate the scene structure based on file type and content.
        
        Args:
            content: The script content
            file_type: The file extension
            
        Returns:
            List of ValidationIssue objects
        """
        issues = []
        
        # Check for scene headers in standard screenplay format
        if file_type in ['.fdx', '.fountain']:
            # For screenplay formats, check for proper scene headers
            # This is a simplified check - real implementation would be more sophisticated
            lines = content.split('\n')
            scene_headers = [l for l in lines if l.strip().startswith('INT.') or l.strip().startswith('EXT.')]
            
            if not scene_headers:
                issues.append(ValidationIssue(
                    issue_type="missing_scene_headers",
                    description="No standard scene headers (INT./EXT.) found",
                    location="entire script",
                    severity="medium",
                    suggestions=[
                        "Add proper scene headers starting with INT. or EXT.",
                        "Format scene headings according to screenplay standards"
                    ]
                ))
        
        # Additional structure checks would go here
        
        return issues
    
    def _validate_continuity(self, content: str) -> List[ValidationIssue]:
        """
        Check for continuity issues in the script.
        
        Args:
            content: The script content
            
        Returns:
            List of ValidationIssue objects
        """
        # In a real implementation, this would parse the script and check for
        # continuity issues like time jumps, character appearances/disappearances, etc.
        # This is a simplified placeholder.
        return []
    
    def _validate_character_consistency(self, content: str) -> List[ValidationIssue]:
        """
        Check for character consistency issues.
        
        Args:
            content: The script content
            
        Returns:
            List of ValidationIssue objects
        """
        # In a real implementation, this would extract character names and
        # check for consistency in naming, dialogue style, etc.
        # This is a simplified placeholder.
        return []
    
    def _analyze_with_gemini(self, content: str) -> List[ValidationIssue]:
        """
        Use Gemini API to analyze the script for issues.
        
        Args:
            content: The script content
            
        Returns:
            List of ValidationIssue objects
        """
        issues = []
        
        if not self.gemini_model:
            return issues
        
        try:
            # Prepare content for Gemini (truncate if too long)
            max_length = 30000  # Adjust based on model limits
            if len(content) > max_length:
                analysis_content = content[:max_length] + "...[truncated]"
                logger.warning(f"Script content truncated from {len(content)} to {max_length} characters for Gemini analysis")
            else:
                analysis_content = content
            
            # Create a prompt for script analysis
            prompt = f"""
            Analyze the following script content for potential issues:
            
            1. Identify continuity problems (e.g., objects appearing/disappearing, time inconsistencies)
            2. Check for character consistency issues
            3. Identify structural problems in the narrative
            4. Look for logical flaws or plot holes
            
            Respond in JSON format with found issues, each containing:
            - issue_type: The category of issue
            - description: Clear description of the problem
            - location: Where in the script the issue occurs
            - severity: "high", "medium", or "low"
            - suggestions: Array of suggestions to fix the issue
            
            Script content:
            {analysis_content}
            """
            
            # Generate response from Gemini
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the response
            # Note: In a production system, we'd need more robust parsing and error handling
            try:
                # Extract JSON from response
                response_text = response.text
                # Find JSON content between triple backticks if present
                if "```json" in response_text and "```" in response_text.split("```json", 1)[1]:
                    json_str = response_text.split("```json", 1)[1].split("```", 1)[0]
                elif "```" in response_text and "```" in response_text.split("```", 1)[1]:
                    json_str = response_text.split("```", 1)[1].split("```", 1)[0]
                else:
                    json_str = response_text
                
                # Clean up the string to ensure it's valid JSON
                json_str = json_str.strip()
                
                # Parse JSON
                result = json.loads(json_str)
                
                # Convert to ValidationIssue objects
                if isinstance(result, list):
                    for item in result:
                        issues.append(ValidationIssue(
                            issue_type=item.get('issue_type', 'unknown'),
                            description=item.get('description', 'No description provided'),
                            location=item.get('location', 'unknown'),
                            severity=item.get('severity', 'medium'),
                            suggestions=item.get('suggestions', [])
                        ))
                elif isinstance(result, dict) and 'issues' in result:
                    for item in result['issues']:
                        issues.append(ValidationIssue(
                            issue_type=item.get('issue_type', 'unknown'),
                            description=item.get('description', 'No description provided'),
                            location=item.get('location', 'unknown'),
                            severity=item.get('severity', 'medium'),
                            suggestions=item.get('suggestions', [])
                        ))
            except Exception as e:
                logger.error(f"Error parsing Gemini response: {e}")
                issues.append(ValidationIssue(
                    issue_type="gemini_parsing_error",
                    description=f"Error parsing Gemini analysis response",
                    location="analysis system",
                    severity="low",
                    suggestions=["Check Gemini API service status", "Try analyzing a shorter script"]
                ))
                
        except Exception as e:
            logger.error(f"Error during Gemini analysis: {e}")
            issues.append(ValidationIssue(
                issue_type="gemini_analysis_error",
                description=f"Error during Gemini analysis: {str(e)}",
                location="analysis system",
                severity="low",
                suggestions=["Check Gemini API configuration", "Verify API key is valid"]
            ))
            
        return issues


if __name__ == "__main__":
    # Simple command line interface
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate script files for structure and continuity issues')
    parser.add_argument('file', help='Path to the script file to validate')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--format', choices=['json', 'html'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    try:
        validator = SceneValidator(config_path=args.config)
        result = validator.validate_file(args.file)
        print(result.get_report(format=args.format))
    except Exception as e:
        print(f"Error: {e}")
        exit(1)