import xml.etree.ElementTree as ET


def extract_document(prop: str) -> ET:
    """
    Extracts an HTML Document 
    from an Openbis ELN entry
    """
    ET.parse(prop)
    breakpoint()