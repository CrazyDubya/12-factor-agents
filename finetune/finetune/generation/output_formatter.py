"""
Output Formatter for Generated Documents

Handles formatting of generated text into structured document formats
with proper metadata, validation, and export capabilities.
"""

import json
import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


class DocumentFormat(Enum):
    """Supported output formats for generated documents."""
    STRUCTURED = "structured"  # Full structured format with metadata
    PLAIN = "plain"            # Plain text only
    JSON = "json"              # JSON format
    MARKDOWN = "markdown"      # Markdown format
    HTML = "html"              # HTML format


@dataclass
class DocumentMetadata:
    """Metadata structure for generated documents."""
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    document_type: str = "unknown"
    world_id: Optional[str] = None
    character_names: List[str] = None
    locations: List[str] = None
    events: List[str] = None
    generation_timestamp: Optional[float] = None
    coherence_score: Optional[float] = None
    word_count: int = 0

    def __post_init__(self):
        if self.character_names is None:
            self.character_names = []
        if self.locations is None:
            self.locations = []
        if self.events is None:
            self.events = []


class OutputFormatter:
    """
    Advanced output formatter for generated narrative documents.

    Features:
    - Multiple output formats (JSON, Markdown, HTML, plain text)
    - Structured document parsing
    - Metadata extraction and validation
    - Export capabilities
    - Batch formatting
    """

    def __init__(self):
        # Document type templates for structured parsing
        self.document_templates = {
            "chronicle": {
                "markers": ["<|chronicle|>", "<|end_chronicle|>"],
                "fields": ["title", "date"],
                "format": "formal"
            },
            "diary": {
                "markers": ["<|diary_entry|>", "<|end_diary|>"],
                "fields": ["author", "date"],
                "format": "personal"
            },
            "letter": {
                "markers": ["<|letter|>", "<|end_letter|>"],
                "fields": ["from", "to", "date"],
                "format": "correspondence"
            },
            "news_article": {
                "markers": ["<|news_article|>", "<|end_news|>"],
                "fields": ["headline", "reporter", "date"],
                "format": "journalism"
            },
            "legal_document": {
                "markers": ["<|legal_document|>", "<|end_legal|>"],
                "fields": ["document", "date"],
                "format": "legal"
            },
            "song": {
                "markers": ["<|song|>", "<|end_song|>"],
                "fields": ["title", "artist"],
                "format": "artistic"
            },
            "map": {
                "markers": ["<|map|>", "<|end_map|>"],
                "fields": ["map"],
                "format": "descriptive"
            },
            "inventory": {
                "markers": ["<|inventory|>", "<|end_inventory|>"],
                "fields": ["location", "date"],
                "format": "list"
            },
            "treaty": {
                "markers": ["<|treaty|>", "<|end_treaty|>"],
                "fields": ["treaty", "parties", "date"],
                "format": "legal"
            },
            "speech": {
                "markers": ["<|speech|>", "<|end_speech|>"],
                "fields": ["speaker", "occasion", "date"],
                "format": "oratory"
            }
        }

    def format_document(
        self,
        text: str,
        document_type: str = "unknown",
        output_format: DocumentFormat = DocumentFormat.STRUCTURED,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Format generated text into structured document.

        Args:
            text: Generated text content
            document_type: Type of document
            output_format: Desired output format
            metadata: Additional metadata

        Returns:
            Formatted document dictionary
        """

        # Parse the generated text
        parsed_content = self._parse_generated_text(text, document_type)

        # Extract or create metadata
        doc_metadata = self._extract_metadata(parsed_content, document_type, metadata)

        # Create base document structure
        document = {
            "content": parsed_content.get("content", text),
            "document_type": document_type,
            "metadata": doc_metadata.__dict__,
        }

        # Apply formatting based on output format
        if output_format == DocumentFormat.STRUCTURED:
            return self._format_structured(document, parsed_content)
        elif output_format == DocumentFormat.PLAIN:
            return self._format_plain(document)
        elif output_format == DocumentFormat.JSON:
            return self._format_json(document)
        elif output_format == DocumentFormat.MARKDOWN:
            return self._format_markdown(document, parsed_content)
        elif output_format == DocumentFormat.HTML:
            return self._format_html(document, parsed_content)
        else:
            return document

    def format_document_collection(
        self,
        documents: List[Dict[str, Any]],
        output_format: DocumentFormat = DocumentFormat.STRUCTURED,
        include_summary: bool = True,
    ) -> Dict[str, Any]:
        """Format a collection of documents with optional summary."""

        formatted_documents = []
        total_word_count = 0
        document_types = {}

        for doc in documents:
            # Format individual document
            formatted_doc = self.format_document(
                doc.get("content", ""),
                doc.get("document_type", "unknown"),
                output_format,
                doc.get("metadata", {})
            )
            formatted_documents.append(formatted_doc)

            # Collect statistics
            word_count = formatted_doc.get("metadata", {}).get("word_count", 0)
            total_word_count += word_count

            doc_type = formatted_doc.get("document_type", "unknown")
            document_types[doc_type] = document_types.get(doc_type, 0) + 1

        collection = {
            "documents": formatted_documents,
            "collection_metadata": {
                "total_documents": len(documents),
                "total_word_count": total_word_count,
                "document_types": document_types,
                "created_at": time.time(),
            }
        }

        if include_summary:
            collection["summary"] = self._create_collection_summary(formatted_documents)

        return collection

    def _parse_generated_text(self, text: str, document_type: str) -> Dict[str, Any]:
        """Parse generated text to extract structure and content."""

        parsed = {
            "raw_text": text,
            "content": text,
            "fields": {},
            "has_structure": False,
        }

        # Check if document type has known structure
        if document_type in self.document_templates:
            template = self.document_templates[document_type]
            markers = template["markers"]
            fields = template["fields"]

            # Look for document markers
            start_marker, end_marker = markers
            if start_marker in text:
                parsed["has_structure"] = True

                # Extract content between markers
                if end_marker in text:
                    start_idx = text.find(start_marker) + len(start_marker)
                    end_idx = text.find(end_marker)
                    structured_content = text[start_idx:end_idx].strip()
                else:
                    start_idx = text.find(start_marker) + len(start_marker)
                    structured_content = text[start_idx:].strip()

                # Parse structured fields
                content_lines = structured_content.split('\n')
                content_start_idx = 0

                for i, line in enumerate(content_lines):
                    line = line.strip()
                    if ':' in line:
                        field_name, field_value = line.split(':', 1)
                        field_name = field_name.strip().lower()
                        field_value = field_value.strip()

                        # Check if this is a known field for this document type
                        if any(field_name.startswith(f.lower()) for f in fields):
                            parsed["fields"][field_name] = field_value
                            content_start_idx = i + 1
                        else:
                            break  # Start of actual content
                    elif line == "":
                        content_start_idx = i + 1
                        break  # Empty line indicates start of content
                    else:
                        break  # Content starts here

                # Extract the actual content
                content_lines = content_lines[content_start_idx:]
                parsed["content"] = '\n'.join(content_lines).strip()

        return parsed

    def _extract_metadata(
        self,
        parsed_content: Dict[str, Any],
        document_type: str,
        additional_metadata: Optional[Dict] = None,
    ) -> DocumentMetadata:
        """Extract metadata from parsed content and additional sources."""

        metadata = DocumentMetadata(document_type=document_type)

        # Set generation timestamp
        metadata.generation_timestamp = time.time()

        # Extract from parsed fields
        fields = parsed_content.get("fields", {})

        for field_name, field_value in fields.items():
            if "title" in field_name:
                metadata.title = field_value
            elif "author" in field_name:
                metadata.author = field_value
            elif any(date_word in field_name for date_word in ["date", "time", "when"]):
                metadata.date = field_value
            elif "from" in field_name or "sender" in field_name:
                metadata.author = field_value
            elif "speaker" in field_name:
                metadata.author = field_value
            elif "artist" in field_name:
                metadata.author = field_value

        # Extract entities from content
        content = parsed_content.get("content", "")
        metadata.character_names = self._extract_character_names(content)
        metadata.locations = self._extract_locations(content)
        metadata.events = self._extract_events(content)

        # Calculate word count
        metadata.word_count = len(content.split()) if content else 0

        # Merge additional metadata
        if additional_metadata:
            for key, value in additional_metadata.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)

        return metadata

    def _extract_character_names(self, text: str) -> List[str]:
        """Extract character names from text."""
        # Look for capitalized words that could be names
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_names = re.findall(name_pattern, text)

        # Filter out common non-name words
        common_words = {
            "The", "This", "That", "And", "But", "When", "Where", "Who", "What", "How",
            "Today", "Tomorrow", "Yesterday", "Morning", "Afternoon", "Evening", "Night",
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
            "January", "February", "March", "April", "May", "June", "July", "August",
            "September", "October", "November", "December", "Spring", "Summer", "Autumn", "Winter"
        }

        character_names = []
        for name in potential_names[:10]:  # Limit to first 10 to avoid noise
            if name not in common_words and len(name) > 2:
                character_names.append(name)

        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in character_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)

        return unique_names

    def _extract_locations(self, text: str) -> List[str]:
        """Extract location names from text."""
        # Simple pattern for potential place names
        location_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:City|Town|Village|Castle|Palace|Kingdom|Empire|Province|County|District)\b',
            r'\bthe\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Mountains|Hills|Forest|Woods|River|Lake|Sea|Ocean|Desert|Plains)\b',
        ]

        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            locations.extend(matches[:5])  # Limit to avoid noise

        return list(set(locations))  # Remove duplicates

    def _extract_events(self, text: str) -> List[str]:
        """Extract events or actions from text."""
        # Look for action verbs and event indicators
        event_patterns = [
            r'\b(?:battle|war|siege|coronation|wedding|funeral|festival|ceremony|meeting|council|treaty|agreement)\b',
            r'\b(?:discovered|founded|established|declared|announced|proclaimed|decided|resolved)\b',
        ]

        events = []
        for pattern in event_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            events.extend(matches[:5])  # Limit to avoid noise

        return list(set(events))  # Remove duplicates

    # Format-specific methods

    def _format_structured(self, document: Dict, parsed_content: Dict) -> Dict[str, Any]:
        """Format as structured document with all metadata."""
        structured_doc = document.copy()

        # Add parsed structure information
        structured_doc["structure"] = {
            "has_explicit_structure": parsed_content.get("has_structure", False),
            "fields": parsed_content.get("fields", {}),
            "content_type": self.document_templates.get(document["document_type"], {}).get("format", "unknown")
        }

        return structured_doc

    def _format_plain(self, document: Dict) -> Dict[str, Any]:
        """Format as plain text document."""
        return {
            "content": document["content"],
            "document_type": document["document_type"],
            "word_count": document["metadata"]["word_count"],
        }

    def _format_json(self, document: Dict) -> Dict[str, Any]:
        """Format as JSON-serializable document."""
        # Ensure all values are JSON-serializable
        json_doc = {}

        for key, value in document.items():
            if isinstance(value, dict):
                json_doc[key] = self._make_json_serializable(value)
            elif isinstance(value, list):
                json_doc[key] = [self._make_json_serializable(item) for item in value]
            else:
                json_doc[key] = value

        return json_doc

    def _format_markdown(self, document: Dict, parsed_content: Dict) -> Dict[str, Any]:
        """Format as Markdown document."""
        content = document["content"]
        metadata = document["metadata"]
        doc_type = document["document_type"]

        # Build Markdown content
        markdown_lines = []

        # Title
        if metadata.get("title"):
            markdown_lines.append(f"# {metadata['title']}")
            markdown_lines.append("")

        # Metadata section
        markdown_lines.append("## Document Information")
        markdown_lines.append("")
        markdown_lines.append(f"- **Type**: {doc_type.title()}")
        if metadata.get("author"):
            markdown_lines.append(f"- **Author**: {metadata['author']}")
        if metadata.get("date"):
            markdown_lines.append(f"- **Date**: {metadata['date']}")
        markdown_lines.append(f"- **Word Count**: {metadata.get('word_count', 0)}")
        markdown_lines.append("")

        # Content
        markdown_lines.append("## Content")
        markdown_lines.append("")
        markdown_lines.append(content)

        # Characters and locations (if any)
        if metadata.get("character_names"):
            markdown_lines.append("")
            markdown_lines.append("## Characters")
            for char in metadata["character_names"]:
                markdown_lines.append(f"- {char}")

        if metadata.get("locations"):
            markdown_lines.append("")
            markdown_lines.append("## Locations")
            for loc in metadata["locations"]:
                markdown_lines.append(f"- {loc}")

        markdown_content = "\n".join(markdown_lines)

        return {
            "content": markdown_content,
            "document_type": doc_type,
            "format": "markdown",
            "metadata": metadata,
        }

    def _format_html(self, document: Dict, parsed_content: Dict) -> Dict[str, Any]:
        """Format as HTML document."""
        content = document["content"]
        metadata = document["metadata"]
        doc_type = document["document_type"]

        # Build HTML content
        html_parts = []

        # HTML head
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='en'>")
        html_parts.append("<head>")
        html_parts.append("<meta charset='UTF-8'>")
        html_parts.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")

        title = metadata.get("title", f"{doc_type.title()} Document")
        html_parts.append(f"<title>{title}</title>")

        # Basic CSS
        html_parts.append("""
        <style>
            body { font-family: Georgia, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; }
            .metadata { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .content { text-align: justify; }
            .characters, .locations { margin-top: 20px; }
            ul { list-style-type: none; padding-left: 0; }
            li { padding: 5px 0; }
        </style>
        """)

        html_parts.append("</head>")
        html_parts.append("<body>")

        # Header
        html_parts.append("<div class='header'>")
        if metadata.get("title"):
            html_parts.append(f"<h1>{metadata['title']}</h1>")
        html_parts.append(f"<h2>{doc_type.replace('_', ' ').title()}</h2>")
        html_parts.append("</div>")

        # Metadata
        html_parts.append("<div class='metadata'>")
        html_parts.append("<h3>Document Information</h3>")
        if metadata.get("author"):
            html_parts.append(f"<p><strong>Author:</strong> {metadata['author']}</p>")
        if metadata.get("date"):
            html_parts.append(f"<p><strong>Date:</strong> {metadata['date']}</p>")
        html_parts.append(f"<p><strong>Word Count:</strong> {metadata.get('word_count', 0)}</p>")
        html_parts.append("</div>")

        # Content
        html_parts.append("<div class='content'>")
        html_parts.append("<h3>Content</h3>")

        # Convert content to HTML paragraphs
        content_paragraphs = content.split('\n\n')
        for paragraph in content_paragraphs:
            if paragraph.strip():
                html_parts.append(f"<p>{paragraph.strip()}</p>")

        html_parts.append("</div>")

        # Characters and locations
        if metadata.get("character_names"):
            html_parts.append("<div class='characters'>")
            html_parts.append("<h3>Characters</h3>")
            html_parts.append("<ul>")
            for char in metadata["character_names"]:
                html_parts.append(f"<li>{char}</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")

        if metadata.get("locations"):
            html_parts.append("<div class='locations'>")
            html_parts.append("<h3>Locations</h3>")
            html_parts.append("<ul>")
            for loc in metadata["locations"]:
                html_parts.append(f"<li>{loc}</li>")
            html_parts.append("</ul>")
            html_parts.append("</div>")

        html_parts.append("</body>")
        html_parts.append("</html>")

        html_content = "\n".join(html_parts)

        return {
            "content": html_content,
            "document_type": doc_type,
            "format": "html",
            "metadata": metadata,
        }

    def _create_collection_summary(self, documents: List[Dict]) -> Dict[str, Any]:
        """Create summary of document collection."""
        summary = {
            "overview": {},
            "characters": {},
            "locations": {},
            "themes": [],
        }

        all_characters = []
        all_locations = []
        total_words = 0

        for doc in documents:
            metadata = doc.get("metadata", {})

            # Collect characters
            chars = metadata.get("character_names", [])
            all_characters.extend(chars)

            # Collect locations
            locs = metadata.get("locations", [])
            all_locations.extend(locs)

            # Sum word counts
            total_words += metadata.get("word_count", 0)

        # Character frequency
        char_counts = {}
        for char in all_characters:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Location frequency
        loc_counts = {}
        for loc in all_locations:
            loc_counts[loc] = loc_counts.get(loc, 0) + 1

        summary["overview"] = {
            "total_documents": len(documents),
            "total_words": total_words,
            "unique_characters": len(set(all_characters)),
            "unique_locations": len(set(all_locations)),
        }

        summary["characters"] = dict(sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        summary["locations"] = dict(sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        return summary

    def _make_json_serializable(self, obj):
        """Make an object JSON-serializable."""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return obj

    # Export methods

    def export_document(
        self,
        document: Dict[str, Any],
        output_path: Union[str, Path],
        format_type: str = "json",
    ):
        """Export document to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(document, f, indent=2, ensure_ascii=False)

        elif format_type.lower() == "yaml":
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(document, f, default_flow_style=False, allow_unicode=True)

        elif format_type.lower() in ["txt", "text"]:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(document.get("content", ""))

        elif format_type.lower() == "md":
            md_doc = self.format_document(
                document.get("content", ""),
                document.get("document_type", "unknown"),
                DocumentFormat.MARKDOWN,
                document.get("metadata", {}),
            )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_doc["content"])

        elif format_type.lower() == "html":
            html_doc = self.format_document(
                document.get("content", ""),
                document.get("document_type", "unknown"),
                DocumentFormat.HTML,
                document.get("metadata", {}),
            )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_doc["content"])

        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def export_collection(
        self,
        collection: Dict[str, Any],
        output_dir: Union[str, Path],
        format_type: str = "json",
        individual_files: bool = True,
    ):
        """Export document collection to files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        documents = collection.get("documents", [])

        if individual_files:
            # Export each document separately
            for i, doc in enumerate(documents):
                doc_type = doc.get("document_type", "document")
                title = doc.get("metadata", {}).get("title", f"document_{i+1}")
                safe_title = re.sub(r'[^\w\-_.]', '_', title)

                filename = f"{doc_type}_{safe_title}.{format_type}"
                file_path = output_dir / filename

                self.export_document(doc, file_path, format_type)

        # Also export collection as a whole
        collection_file = output_dir / f"collection.{format_type}"
        if format_type.lower() == "json":
            with open(collection_file, "w", encoding="utf-8") as f:
                json.dump(collection, f, indent=2, ensure_ascii=False)
        elif format_type.lower() == "yaml":
            with open(collection_file, "w", encoding="utf-8") as f:
                yaml.dump(collection, f, default_flow_style=False, allow_unicode=True)