#!/usr/bin/env python3
"""
StoryboardGen - Generate storyboards from script text using Gemini API
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('StoryboardGen')

@dataclass
class StoryboardFrame:
    """Class to represent a single storyboard frame."""
    scene_number: str
    description: str
    image_path: Optional[str] = None
    camera_angle: str = "Medium Shot"
    camera_movement: str = "Static"
    characters: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.characters is None:
            self.characters = []


class StoryboardGenerator:
    """Main class for generating storyboards from scripts."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the storyboard generator.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = {}
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Set up Gemini API
        api_key = self.config.get('gemini_api_key', os.environ.get('GEMINI_API_KEY'))
        if not api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable or provide in config.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config.get('gemini_model', 'gemini-pro'))
        self.image_model = genai.GenerativeModel(self.config.get('gemini_image_model', 'gemini-pro-vision'))
    
    def parse_script(self, script_path: str) -> List[Dict[str, Any]]:
        """
        Parse a script file into scenes.
        
        Args:
            script_path: Path to script file
            
        Returns:
            List of scenes with metadata
        """
        logger.info(f"Parsing script: {script_path}")
        
        # Read the script file
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Extract file extension to determine format
        file_extension = os.path.splitext(script_path)[1].lower()
        
        # Use Gemini to parse the script
        prompt = f"""
        Parse the following script into a structured format with scenes.
        For each scene, identify:
        1. Scene number
        2. Location (INT/EXT)
        3. Time of day
        4. Description
        5. Characters present
        6. Key visual elements
        7. Camera suggestions
        
        Format your response as a JSON array of scene objects.
        
        Script content:
        {script_content[:50000]}  # Limit content length for API
        """
        
        response = self.model.generate_content(prompt)
        
        try:
            # Extract JSON from response
            scenes_text = response.text
            # Find JSON array in response
            start_idx = scenes_text.find('[')
            end_idx = scenes_text.rfind(']') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_text = scenes_text[start_idx:end_idx]
                scenes = json.loads(json_text)
            else:
                # Fallback if JSON not found
                logger.warning("Could not extract JSON array from response. Using default scene structure.")
                scenes = [{"scene_number": "1", "description": "Default scene", "characters": []}]
        except Exception as e:
            logger.error(f"Error parsing scene JSON: {str(e)}")
            scenes = [{"scene_number": "1", "description": "Default scene", "characters": []}]
        
        logger.info(f"Parsed {len(scenes)} scenes from script")
        return scenes
    
    def generate_from_script(self, script_path: str, output_dir: Optional[str] = None) -> 'Storyboard':
        """
        Generate a storyboard from a script file.
        
        Args:
            script_path: Path to script file
            output_dir: Directory to save generated images
            
        Returns:
            Storyboard object
        """
        logger.info(f"Generating storyboard from script: {script_path}")
        
        # Create output directory if needed
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = os.path.join(os.path.dirname(script_path), 'storyboard')
            os.makedirs(output_dir, exist_ok=True)
        
        # Parse script into scenes
        scenes = self.parse_script(script_path)
        
        # Create storyboard frames
        frames = []
        for scene in scenes:
            # Generate image for scene
            image_path = None
            if self.config.get('generate_images', True):
                image_path = self._generate_image_for_scene(scene, output_dir)
            
            # Create frame
            frame = StoryboardFrame(
                scene_number=scene.get('scene_number', ''),
                description=scene.get('description', ''),
                image_path=image_path,
                camera_angle=scene.get('camera_suggestions', {}).get('angle', 'Medium Shot'),
                camera_movement=scene.get('camera_suggestions', {}).get('movement', 'Static'),
                characters=scene.get('characters', []),
                notes=scene.get('key_visual_elements', '')
            )
            frames.append(frame)
        
        # Create storyboard
        storyboard = Storyboard(
            title=os.path.basename(script_path),
            frames=frames,
            output_dir=output_dir
        )
        
        logger.info(f"Created storyboard with {len(frames)} frames")
        return storyboard
    
    def _generate_image_for_scene(self, scene: Dict[str, Any], output_dir: str) -> Optional[str]:
        """
        Generate an image for a scene using Gemini.
        
        Args:
            scene: Scene data
            output_dir: Directory to save generated image
            
        Returns:
            Path to generated image
        """
        try:
            # In a real implementation, this would use Gemini's image generation capabilities
            # For this example, we'll create a placeholder image
            
            scene_num = scene.get('scene_number', '0')
            img_path = os.path.join(output_dir, f"scene_{scene_num}.png")
            
            # Create a placeholder image
            img = Image.new('RGB', (800, 450), color=(240, 240, 240))
            d = ImageDraw.Draw(img)
            
            # Try to load a font, use default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 20)
                small_font = ImageFont.truetype("arial.ttf", 14)
            except IOError:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw scene details
            d.text((20, 20), f"Scene {scene_num}", fill=(0, 0, 0), font=font)
            location = f"{scene.get('location', '')}"
            if scene.get('time_of_day'):
                location += f" - {scene.get('time_of_day')}"
            d.text((20, 50), location, fill=(0, 0, 0), font=font)
            
            # Draw scene description (wrapped)
            description = scene.get('description', '')
            y_pos = 90
            words = description.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                text_width = d.textlength(test_line, font=small_font)
                if text_width > 760:
                    d.text((20, y_pos), line, fill=(0, 0, 0), font=small_font)
                    y_pos += 20
                    line = word + " "
                else:
                    line = test_line
            d.text((20, y_pos), line, fill=(0, 0, 0), font=small_font)
            
            # Draw characters
            y_pos += 40
            d.text((20, y_pos), "Characters:", fill=(0, 0, 0), font=small_font)
            y_pos += 20
            for character in scene.get('characters', [])[:5]:  # Limit to 5 characters
                d.text((40, y_pos), f"- {character}", fill=(0, 0, 0), font=small_font)
                y_pos += 20
            
            # Save the image
            img.save(img_path)
            logger.info(f"Generated placeholder image for scene {scene_num}: {img_path}")
            
            return img_path
        
        except Exception as e:
            logger.error(f"Error generating image for scene {scene.get('scene_number', '')}: {str(e)}")
            return None


class Storyboard:
    """Class to represent a complete storyboard."""
    
    def __init__(self, title: str, frames: List[StoryboardFrame], output_dir: str):
        """
        Initialize the storyboard.
        
        Args:
            title: Storyboard title
            frames: List of storyboard frames
            output_dir: Directory for storyboard outputs
        """
        self.title = title
        self.frames = frames
        self.output_dir = output_dir
    
    def export_pdf(self, output_path: Optional[str] = None) -> str:
        """
        Export the storyboard to a PDF file.
        
        Args:
            output_path: Path for the output PDF
            
        Returns:
            Path to the generated PDF
        """
        if not output_path:
            output_path = os.path.join(self.output_dir, f"{self.title}_storyboard.pdf")
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 18)
        c.drawString(72, height - 72, f"Storyboard: {self.title}")
        
        # Add date
        c.setFont("Helvetica", 12)
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        c.drawString(72, height - 90, f"Generated: {date_str}")
        
        # Set starting position
        y_pos = height - 130
        frames_per_page = 3
        current_frame = 0
        
        # Loop through frames
        for frame in self.frames:
            if current_frame > 0 and current_frame % frames_per_page == 0:
                c.showPage()
                y_pos = height - 72
            
            # Draw frame
            c.setFont("Helvetica-Bold", 12)
            c.drawString(72, y_pos, f"Scene {frame.scene_number}")
            y_pos -= 15
            
            # Draw image if available
            if frame.image_path and os.path.exists(frame.image_path):
                try:
                    c.drawImage(frame.image_path, 72, y_pos - 100, width=450, height=100)
                    y_pos -= 110
                except Exception as e:
                    logger.error(f"Error drawing image: {str(e)}")
                    y_pos -= 20
            
            # Draw description
            c.setFont("Helvetica", 10)
            text_object = c.beginText(72, y_pos)
            text_object.textLine(f"Description: {frame.description[:200]}...")
            text_object.textLine("")
            text_object.textLine(f"Camera: {frame.camera_angle}, {frame.camera_movement}")
            text_object.textLine(f"Characters: {', '.join(frame.characters)}")
            if frame.notes:
                text_object.textLine(f"Notes: {frame.notes}")
            c.drawText(text_object)
            
            y_pos -= 60
            current_frame += 1
        
        c.save()
        logger.info(f"Exported storyboard to PDF: {output_path}")
        return output_path
    
    def export_frames(self, output_dir: Optional[str] = None) -> List[str]:
        """
        Export individual frames as images.
        
        Args:
            output_dir: Directory to save frame images
            
        Returns:
            List of paths to exported frame images
        """
        if not output_dir:
            output_dir = os.path.join(self.output_dir, "frames")
        
        os.makedirs(output_dir, exist_ok=True)
        
        exported_paths = []
        for frame in self.frames:
            if frame.image_path and os.path.exists(frame.image_path):
                output_path = os.path.join(output_dir, f"scene_{frame.scene_number}.png")
                
                # Copy image to output directory
                try:
                    import shutil
                    shutil.copy2(frame.image_path, output_path)
                    exported_paths.append(output_path)
                except Exception as e:
                    logger.error(f"Error exporting frame: {str(e)}")
        
        logger.info(f"Exported {len(exported_paths)} frames to {output_dir}")
        return exported_paths
    
    def export_html(self, output_path: Optional[str] = None) -> str:
        """
        Export the storyboard to an HTML file.
        
        Args:
            output_path: Path for the output HTML
            
        Returns:
            Path to the generated HTML
        """
        if not output_path:
            output_path = os.path.join(self.output_dir, f"{self.title}_storyboard.html")
        
        # Create HTML content
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Storyboard: {self.title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        h1 {{
            color: #333;
        }}
        .frame {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
        }}
        .frame-header {{
            display: flex;
            justify-content: space-between;
        }}
        .frame-image {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
        }}
        .frame-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .frame-description {{
            grid-column: 1 / 3;
        }}
    </style>
</head>
<body>
    <h1>Storyboard: {self.title}</h1>
    <p>Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <div class="storyboard">
"""
        
        # Add frames
        for frame in self.frames:
            image_html = ""
            if frame.image_path:
                # Convert to relative path
                rel_path = os.path.relpath(frame.image_path, os.path.dirname(output_path))
                image_html = f'<img class="frame-image" src="{rel_path}" alt="Scene {frame.scene_number}">'
            
            html += f"""
        <div class="frame">
            <div class="frame-header">
                <h2>Scene {frame.scene_number}</h2>
                <div>{frame.camera_angle}, {frame.camera_movement}</div>
            </div>
            {image_html}
            <div class="frame-details">
                <div class="frame-description">
                    <h3>Description</h3>
                    <p>{frame.description}</p>
                </div>
                <div>
                    <h3>Characters</h3>
                    <ul>
                        {"".join(f"<li>{character}</li>" for character in frame.characters)}
                    </ul>
                </div>
                <div>
                    <h3>Notes</h3>
                    <p>{frame.notes}</p>
                </div>
            </div>
        </div>
"""
        
        # Close HTML
        html += """
    </div>
</body>
</html>
"""
        
        # Write HTML to file
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Exported storyboard to HTML: {output_path}")
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate storyboards from script text')
    parser.add_argument('script_path', help='Path to script file')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--output', help='Output directory for storyboard files')
    parser.add_argument('--format', choices=['pdf', 'html', 'frames', 'all'], default='all',
                        help='Output format (pdf, html, frames, or all)')
    args = parser.parse_args()
    
    try:
        generator = StoryboardGenerator(config_path=args.config)
        storyboard = generator.generate_from_script(args.script_path, args.output)
        
        if args.format == 'pdf' or args.format == 'all':
            storyboard.export_pdf()
        
        if args.format == 'html' or args.format == 'all':
            storyboard.export_html()
        
        if args.format == 'frames' or args.format == 'all':
            storyboard.export_frames()
        
        logger.info("Storyboard generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error generating storyboard: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)