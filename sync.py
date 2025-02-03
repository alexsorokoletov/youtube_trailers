import os
import uuid
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from utils import load_config

# Load configuration
CONFIG_PATH = "config.yaml"
config = load_config(CONFIG_PATH)

TRAILER_FOLDER = config['output_folder']
OUTPUT_XML_FILE = config.get('xml_metadata_path', 'trailers.xml')

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_xml_for_trailers():
    # Create the root element with schema attributes
    root = ET.Element("IntroPluginConfiguration", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
    })
    detected_videos = ET.SubElement(root, "DetectedLocalVideos")

    # List to store generated GUIDs
    generated_guids = []

    # Iterate over files in the trailer folder
    for file_path in Path(TRAILER_FOLDER).glob('*'):
        if file_path.is_file() and file_path.suffix in ['.mp4', '.webm']:
            intro_video = ET.SubElement(detected_videos, "IntroVideo")
            name = ET.SubElement(intro_video, "Name")
            # Use the file name without extension and replace underscores with spaces
            name.text = file_path.stem.replace('_', ' ')

            item_id = ET.SubElement(intro_video, "ItemId")
            guid = str(uuid.uuid4())  # Generate a unique ID
            item_id.text = guid
            generated_guids.append(guid)

    # Add additional elements
    default_local_videos = ET.SubElement(root, "DefaultLocalVideos")
    for guid in generated_guids:
        guid_element = ET.SubElement(default_local_videos, "guid")
        guid_element.text = guid

    ET.SubElement(root, "TagIntros")
    ET.SubElement(root, "GenreIntros")
    ET.SubElement(root, "StudioIntros")
    ET.SubElement(root, "CurrentDateIntros")
    ET.SubElement(root, "PremiereDateIntros")
    ET.SubElement(root, "IntrosForMoviesOnly").text = "false"

    # Prettify and write the XML to a file
    pretty_xml = prettify_xml(root)
    with open(OUTPUT_XML_FILE, "w", encoding="utf-8") as xml_file:
        xml_file.write(pretty_xml)

    print(f"XML file generated: {OUTPUT_XML_FILE}")

if __name__ == "__main__":
    generate_xml_for_trailers()