"""
Output harvesting and parsing utilities.

Extracts structured data from tool outputs:
- JSON parsing
- Code fence extraction
- Unified diff parsing
- Plain text fallback
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple
from conductor.envelopes import Artifact, ArtifactType


class Harvester:
    """Harvests and parses tool outputs into structured artifacts."""

    @staticmethod
    def harvest(content: str, hint: Optional[str] = None) -> List[Artifact]:
        """
        Harvest artifacts from raw content.

        Args:
            content: Raw output content
            hint: Optional hint about expected format

        Returns:
            List of extracted artifacts
        """
        artifacts = []

        # Try JSON first
        json_artifacts = Harvester._extract_json(content)
        artifacts.extend(json_artifacts)

        # Try code fences
        code_artifacts = Harvester._extract_code_fences(content)
        artifacts.extend(code_artifacts)

        # Try unified diffs
        diff_artifacts = Harvester._extract_diffs(content)
        artifacts.extend(diff_artifacts)

        # If nothing found, treat as plain text
        if not artifacts:
            artifacts.append(
                Artifact(
                    type=ArtifactType.TEXT,
                    content=content,
                    metadata={"format": "plain"},
                )
            )

        return artifacts

    @staticmethod
    def _extract_json(content: str) -> List[Artifact]:
        """Extract JSON objects from content."""
        artifacts = []

        # Try parsing entire content as JSON
        try:
            data = json.loads(content)
            artifacts.append(
                Artifact(
                    type=ArtifactType.JSON,
                    content=json.dumps(data, indent=2),
                    metadata={"format": "json", "validated": True},
                )
            )
            return artifacts
        except json.JSONDecodeError:
            pass

        # Try extracting JSON blocks (```json ... ```)
        json_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_pattern, content, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                artifacts.append(
                    Artifact(
                        type=ArtifactType.JSON,
                        content=json.dumps(data, indent=2),
                        metadata={"format": "json_fence", "validated": True},
                    )
                )
            except json.JSONDecodeError:
                pass

        return artifacts

    @staticmethod
    def _extract_code_fences(content: str) -> List[Artifact]:
        """Extract code blocks from markdown fences."""
        artifacts = []

        # Pattern: ```language\ncode\n```
        fence_pattern = r'```(\w+)?\s*\n(.*?)\n```'
        matches = re.findall(fence_pattern, content, re.DOTALL)

        for lang, code in matches:
            # Determine artifact type from language
            artifact_type = ArtifactType.TEXT
            if lang in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'rust', 'go']:
                artifact_type = ArtifactType.TEXT
            elif lang == 'json':
                artifact_type = ArtifactType.JSON
            elif lang in ['diff', 'patch']:
                artifact_type = ArtifactType.PATCH

            artifacts.append(
                Artifact(
                    type=artifact_type,
                    content=code,
                    metadata={"format": "code_fence", "language": lang or "unknown"},
                )
            )

        return artifacts

    @staticmethod
    def _extract_diffs(content: str) -> List[Artifact]:
        """Extract unified diff patches."""
        artifacts = []

        # Pattern for unified diff header
        diff_pattern = r'(?:diff --git|---|\+\+\+).*?(?=\n(?:diff --git|$))'
        matches = re.findall(diff_pattern, content, re.DOTALL)

        for match in matches:
            if match.strip():
                artifacts.append(
                    Artifact(
                        type=ArtifactType.PATCH,
                        content=match,
                        metadata={"format": "unified_diff"},
                    )
                )

        return artifacts

    @staticmethod
    def extract_key_value_pairs(content: str) -> Dict[str, str]:
        """Extract key-value pairs from text (key: value format)."""
        pairs = {}
        pattern = r'^(\w+):\s*(.+)$'

        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                key, value = match.groups()
                pairs[key] = value

        return pairs
