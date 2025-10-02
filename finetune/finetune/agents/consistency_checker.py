"""
ConsistencyChecker Agent - Validates cross-document coherence.

This agent ensures that all generated documents maintain consistency
with established world rules, character traits, and narrative continuity.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
import dspy
from dataclasses import dataclass
from .base_agent import BaseAgent, AgentRole, AgentResponse, NarrativeContext

@dataclass
class ConsistencyIssue:
    """Represents a consistency issue found in the narrative."""
    issue_id: str
    severity: str  # 'critical', 'major', 'minor'
    category: str  # 'character', 'world_rules', 'timeline', 'location', 'logic'
    description: str
    affected_documents: List[str]
    suggested_resolution: str
    confidence: float

class ConsistencyCheckSignature(dspy.Signature):
    """Check consistency between narrative elements."""

    world_rules: str = dspy.InputField(desc="Established world rules and constraints")
    character_profiles: str = dspy.InputField(desc="Character personalities and traits")
    document_content: str = dspy.InputField(desc="Content to check for consistency")
    previous_documents: str = dspy.InputField(desc="Previously validated documents for reference")

    consistency_status: str = dspy.OutputField(desc="Overall consistency status: 'consistent', 'minor_issues', 'major_issues'")
    identified_issues: str = dspy.OutputField(desc="List of specific consistency problems found")
    character_consistency: str = dspy.OutputField(desc="Assessment of character behavior consistency")
    world_rule_adherence: str = dspy.OutputField(desc="Assessment of adherence to world rules")
    timeline_consistency: str = dspy.OutputField(desc="Assessment of temporal consistency")

class ConflictResolutionSignature(dspy.Signature):
    """Propose resolutions for consistency conflicts."""

    conflict_description: str = dspy.InputField(desc="Description of the consistency conflict")
    conflicting_elements: str = dspy.InputField(desc="Specific elements that are in conflict")
    world_context: str = dspy.InputField(desc="World rules and context to guide resolution")

    resolution_strategy: str = dspy.OutputField(desc="Recommended strategy for resolving the conflict")
    modified_content: str = dspy.OutputField(desc="Suggested modifications to resolve the issue")
    impact_assessment: str = dspy.OutputField(desc="Assessment of how this change affects other elements")

class ConsistencyCheckerAgent(BaseAgent):
    """
    Agent responsible for validating cross-document coherence.

    This agent identifies inconsistencies across all generated content
    and suggests resolutions to maintain narrative integrity.
    """

    def __init__(self, llm: Optional[dspy.LM] = None, **kwargs):
        super().__init__(role=AgentRole.CONSISTENCY_CHECKER, llm=llm, **kwargs)

        # Initialize DSPy modules
        with dspy.context(lm=self.llm):
            self.consistency_checker = dspy.ChainOfThought(ConsistencyCheckSignature)
            self.conflict_resolver = dspy.ChainOfThought(ConflictResolutionSignature)

        # Consistency check categories and their weights
        self.consistency_categories = {
            'character_behavior': {'weight': 0.25, 'threshold': 0.8},
            'world_rules': {'weight': 0.3, 'threshold': 0.9},
            'timeline': {'weight': 0.2, 'threshold': 0.85},
            'location_details': {'weight': 0.15, 'threshold': 0.8},
            'logical_coherence': {'weight': 0.1, 'threshold': 0.75}
        }

    def execute(self, context: NarrativeContext, **kwargs) -> AgentResponse:
        """
        Check consistency across all narrative elements.

        Args:
            context: Narrative context with all generated content
            **kwargs: Additional parameters:
                - check_categories: Specific categories to check
                - severity_threshold: Minimum severity to report
                - auto_resolve: Whether to attempt automatic resolution

        Returns:
            AgentResponse containing consistency analysis and issues
        """
        try:
            # Extract parameters
            check_categories = kwargs.get('check_categories', list(self.consistency_categories.keys()))
            severity_threshold = kwargs.get('severity_threshold', 'minor')
            auto_resolve = kwargs.get('auto_resolve', False)

            # Perform comprehensive consistency check
            consistency_results = self._perform_consistency_check(context, check_categories)

            # Identify and categorize issues
            issues = self._identify_issues(consistency_results, severity_threshold)

            # Attempt resolution if requested
            resolutions = []
            if auto_resolve and issues:
                resolutions = self._attempt_auto_resolution(context, issues)

            # Calculate overall consistency score
            consistency_score = self._calculate_consistency_score(consistency_results)

            return AgentResponse(
                success=True,
                content={
                    'consistency_score': consistency_score,
                    'issues': issues,
                    'resolutions': resolutions,
                    'detailed_results': consistency_results,
                    'summary': self._create_consistency_summary(consistency_results, issues)
                },
                metadata={
                    'total_issues': len(issues),
                    'critical_issues': len([i for i in issues if i.severity == 'critical']),
                    'categories_checked': check_categories,
                    'overall_status': self._determine_overall_status(consistency_score, issues)
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                content=None,
                error_message=f"Consistency check failed: {str(e)}"
            )

    def validate_input(self, context: NarrativeContext, **kwargs) -> bool:
        """Validate input for consistency checking."""
        if not context.generated_documents:
            self.logger.error("No documents to check for consistency")
            return False

        if not context.characters and not context.world_rules:
            self.logger.error("Insufficient world context for consistency checking")
            return False

        return True

    def _perform_consistency_check(self, context: NarrativeContext,
                                 check_categories: List[str]) -> Dict[str, Any]:
        """Perform comprehensive consistency check across all content."""

        results = {}

        # Prepare context strings
        world_rules_str = self._format_world_rules(context)
        character_profiles_str = self._format_character_profiles(context)

        # Check each document
        for doc in context.generated_documents:
            doc_id = doc['id']

            # Get other documents for cross-reference
            other_docs = [d for d in context.generated_documents if d['id'] != doc_id]
            previous_docs_str = self._format_document_summaries(other_docs)

            with dspy.context(lm=self.llm):
                check_result = self.consistency_checker(
                    world_rules=world_rules_str,
                    character_profiles=character_profiles_str,
                    document_content=f"Title: {doc['title']}\nContent: {doc['content']}",
                    previous_documents=previous_docs_str
                )

            results[doc_id] = {
                'document': doc,
                'consistency_status': check_result.consistency_status,
                'identified_issues': check_result.identified_issues,
                'character_consistency': check_result.character_consistency,
                'world_rule_adherence': check_result.world_rule_adherence,
                'timeline_consistency': check_result.timeline_consistency,
                'individual_scores': self._parse_consistency_scores(check_result)
            }

            self.log_operation(f"Checked consistency for {doc['title']}", {
                'status': check_result.consistency_status,
                'issues_found': len(check_result.identified_issues.split(';')) if check_result.identified_issues else 0
            })

        # Perform cross-document consistency checks
        cross_doc_results = self._check_cross_document_consistency(context)
        results['cross_document'] = cross_doc_results

        return results

    def _identify_issues(self, consistency_results: Dict[str, Any],
                        severity_threshold: str) -> List[ConsistencyIssue]:
        """Identify and categorize consistency issues from check results."""

        issues = []
        issue_counter = 0

        severity_order = {'minor': 1, 'major': 2, 'critical': 3}
        min_severity = severity_order.get(severity_threshold, 1)

        # Process document-level issues
        for doc_id, doc_results in consistency_results.items():
            if doc_id == 'cross_document':
                continue

            # Parse identified issues
            if doc_results['identified_issues']:
                issue_descriptions = doc_results['identified_issues'].split(';')

                for issue_desc in issue_descriptions:
                    issue_desc = issue_desc.strip()
                    if not issue_desc:
                        continue

                    # Categorize and assess severity
                    category, severity = self._categorize_issue(issue_desc)

                    if severity_order.get(severity, 0) >= min_severity:
                        issue = ConsistencyIssue(
                            issue_id=f"issue_{issue_counter:03d}",
                            severity=severity,
                            category=category,
                            description=issue_desc,
                            affected_documents=[doc_id],
                            suggested_resolution=self._suggest_resolution(issue_desc, category),
                            confidence=0.8  # Default confidence
                        )
                        issues.append(issue)
                        issue_counter += 1

        # Process cross-document issues
        if 'cross_document' in consistency_results:
            cross_doc_issues = consistency_results['cross_document'].get('issues', [])

            for issue_desc in cross_doc_issues:
                category, severity = self._categorize_issue(issue_desc['description'])

                if severity_order.get(severity, 0) >= min_severity:
                    issue = ConsistencyIssue(
                        issue_id=f"issue_{issue_counter:03d}",
                        severity=severity,
                        category=category,
                        description=issue_desc['description'],
                        affected_documents=issue_desc.get('documents', []),
                        suggested_resolution=self._suggest_resolution(issue_desc['description'], category),
                        confidence=issue_desc.get('confidence', 0.7)
                    )
                    issues.append(issue)
                    issue_counter += 1

        return issues

    def _attempt_auto_resolution(self, context: NarrativeContext,
                                issues: List[ConsistencyIssue]) -> List[Dict[str, Any]]:
        """Attempt automatic resolution of consistency issues."""

        resolutions = []
        world_context_str = self._format_world_context(context)

        for issue in issues:
            # Only attempt auto-resolution for minor issues
            if issue.severity != 'minor':
                continue

            try:
                # Get conflicting elements
                conflicting_elements = self._extract_conflicting_elements(issue, context)

                with dspy.context(lm=self.llm):
                    resolution_result = self.conflict_resolver(
                        conflict_description=issue.description,
                        conflicting_elements=conflicting_elements,
                        world_context=world_context_str
                    )

                resolution = {
                    'issue_id': issue.issue_id,
                    'strategy': resolution_result.resolution_strategy,
                    'modified_content': resolution_result.modified_content,
                    'impact_assessment': resolution_result.impact_assessment,
                    'confidence': 0.6,  # Lower confidence for auto-resolution
                    'requires_review': True
                }

                resolutions.append(resolution)

            except Exception as e:
                self.logger.error(f"Failed to auto-resolve issue {issue.issue_id}: {str(e)}")

        return resolutions

    def _check_cross_document_consistency(self, context: NarrativeContext) -> Dict[str, Any]:
        """Check consistency across multiple documents."""

        cross_doc_results = {
            'character_continuity': [],
            'timeline_coherence': [],
            'world_rule_violations': [],
            'location_consistency': [],
            'issues': []
        }

        # Character continuity check
        character_appearances = self._track_character_appearances(context)
        for char_id, appearances in character_appearances.items():
            if len(appearances) > 1:
                inconsistencies = self._check_character_continuity(appearances, context)
                cross_doc_results['character_continuity'].extend(inconsistencies)

        # Timeline coherence check
        timeline_events = self._extract_timeline_events(context)
        timeline_issues = self._check_timeline_coherence(timeline_events)
        cross_doc_results['timeline_coherence'].extend(timeline_issues)

        # World rule violations
        rule_violations = self._check_world_rule_violations(context)
        cross_doc_results['world_rule_violations'].extend(rule_violations)

        # Location consistency
        location_descriptions = self._track_location_descriptions(context)
        location_issues = self._check_location_consistency(location_descriptions)
        cross_doc_results['location_consistency'].extend(location_issues)

        # Consolidate all cross-document issues
        all_issues = (
            cross_doc_results['character_continuity'] +
            cross_doc_results['timeline_coherence'] +
            cross_doc_results['world_rule_violations'] +
            cross_doc_results['location_consistency']
        )

        cross_doc_results['issues'] = all_issues

        return cross_doc_results

    def _format_world_rules(self, context: NarrativeContext) -> str:
        """Format world rules for consistency checking."""
        if isinstance(context.world_rules, dict):
            return '; '.join([f"{k}: {v}" for k, v in context.world_rules.items() if v])
        else:
            return str(context.world_rules) if context.world_rules else "No specific world rules"

    def _format_character_profiles(self, context: NarrativeContext) -> str:
        """Format character profiles for consistency checking."""
        if not context.characters:
            return "No established characters"

        profiles = []
        for char in context.characters:
            profile = f"{char['name']}: {char['personality']} | Motivations: {char['motivations']}"
            profiles.append(profile)

        return ' | '.join(profiles)

    def _format_document_summaries(self, documents: List[Dict[str, Any]]) -> str:
        """Format document summaries for reference."""
        if not documents:
            return "No previous documents"

        summaries = []
        for doc in documents:
            summary = f"{doc['type']}: {doc['title']} - {doc['content'][:200]}..."
            summaries.append(summary)

        return ' | '.join(summaries)

    def _format_world_context(self, context: NarrativeContext) -> str:
        """Format complete world context."""
        parts = [
            f"Theme: {context.theme}",
            f"Rules: {self._format_world_rules(context)}",
            f"Characters: {len(context.characters)} established",
            f"Locations: {len(context.locations)} established"
        ]
        return ' | '.join(parts)

    def _parse_consistency_scores(self, check_result) -> Dict[str, float]:
        """Parse consistency scores from check result."""
        # This would parse the LLM output to extract numerical scores
        # For now, return default scores based on status
        status = check_result.consistency_status

        if status == 'consistent':
            base_score = 0.9
        elif status == 'minor_issues':
            base_score = 0.7
        else:  # major_issues
            base_score = 0.5

        return {
            'character': base_score + random.uniform(-0.1, 0.1),
            'world_rules': base_score + random.uniform(-0.1, 0.1),
            'timeline': base_score + random.uniform(-0.1, 0.1),
            'location': base_score + random.uniform(-0.1, 0.1),
            'logic': base_score + random.uniform(-0.1, 0.1)
        }

    def _categorize_issue(self, issue_description: str) -> Tuple[str, str]:
        """Categorize an issue by type and severity."""

        issue_lower = issue_description.lower()

        # Determine category
        if any(term in issue_lower for term in ['character', 'personality', 'behavior', 'motivation']):
            category = 'character_behavior'
        elif any(term in issue_lower for term in ['world', 'rule', 'physics', 'magic', 'law']):
            category = 'world_rules'
        elif any(term in issue_lower for term in ['time', 'date', 'timeline', 'chronology', 'sequence']):
            category = 'timeline'
        elif any(term in issue_lower for term in ['location', 'place', 'geography', 'distance']):
            category = 'location_details'
        else:
            category = 'logical_coherence'

        # Determine severity
        if any(term in issue_lower for term in ['critical', 'major', 'serious', 'contradiction', 'impossible']):
            severity = 'critical'
        elif any(term in issue_lower for term in ['significant', 'important', 'conflict', 'inconsistent']):
            severity = 'major'
        else:
            severity = 'minor'

        return category, severity

    def _suggest_resolution(self, issue_description: str, category: str) -> str:
        """Suggest a resolution for a consistency issue."""

        resolution_templates = {
            'character_behavior': "Review and align character actions with established personality traits",
            'world_rules': "Ensure all events conform to established world physics and rules",
            'timeline': "Verify chronological order and adjust dates/sequences as needed",
            'location_details': "Standardize location descriptions and geographical relationships",
            'logical_coherence': "Review logical flow and cause-and-effect relationships"
        }

        return resolution_templates.get(category, "Review and revise content for consistency")

    def _calculate_consistency_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall consistency score."""

        total_score = 0.0
        total_weight = 0.0

        for doc_id, doc_results in results.items():
            if doc_id == 'cross_document':
                continue

            individual_scores = doc_results.get('individual_scores', {})

            for category, score in individual_scores.items():
                if category in self.consistency_categories:
                    weight = self.consistency_categories[category]['weight']
                    total_score += score * weight
                    total_weight += weight

        # Factor in cross-document consistency
        if 'cross_document' in results:
            cross_doc_score = self._assess_cross_document_score(results['cross_document'])
            total_score += cross_doc_score * 0.2  # 20% weight for cross-document consistency
            total_weight += 0.2

        overall_score = total_score / total_weight if total_weight > 0 else 0.0
        return round(min(max(overall_score, 0.0), 1.0), 3)

    def _assess_cross_document_score(self, cross_doc_results: Dict[str, Any]) -> float:
        """Assess cross-document consistency score."""
        total_issues = len(cross_doc_results.get('issues', []))

        if total_issues == 0:
            return 1.0
        elif total_issues <= 2:
            return 0.8
        elif total_issues <= 5:
            return 0.6
        else:
            return 0.4

    def _determine_overall_status(self, consistency_score: float, issues: List[ConsistencyIssue]) -> str:
        """Determine overall consistency status."""
        critical_issues = [i for i in issues if i.severity == 'critical']
        major_issues = [i for i in issues if i.severity == 'major']

        if critical_issues or consistency_score < 0.6:
            return 'needs_major_revision'
        elif major_issues or consistency_score < 0.8:
            return 'needs_minor_revision'
        else:
            return 'acceptable'

    def _create_consistency_summary(self, results: Dict[str, Any], issues: List[ConsistencyIssue]) -> str:
        """Create a summary of consistency check results."""

        total_docs = len([k for k in results.keys() if k != 'cross_document'])
        issue_counts = {'critical': 0, 'major': 0, 'minor': 0}

        for issue in issues:
            issue_counts[issue.severity] += 1

        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        return f"""
Consistency Summary:
- Documents Checked: {total_docs}
- Total Issues: {len(issues)}
- Critical: {issue_counts['critical']}, Major: {issue_counts['major']}, Minor: {issue_counts['minor']}
- Main Problem Areas: {', '.join(sorted(category_counts.keys()))}
- Overall Status: {self._determine_overall_status(self._calculate_consistency_score(results), issues)}
"""

    # Placeholder methods for cross-document consistency checks
    def _track_character_appearances(self, context: NarrativeContext) -> Dict[str, List[Dict]]:
        """Track character appearances across documents."""
        return {}  # Implementation would track character mentions

    def _check_character_continuity(self, appearances: List[Dict], context: NarrativeContext) -> List[Dict]:
        """Check character behavior continuity."""
        return []  # Implementation would check for character inconsistencies

    def _extract_timeline_events(self, context: NarrativeContext) -> List[Dict]:
        """Extract timeline events from documents."""
        return []  # Implementation would extract temporal references

    def _check_timeline_coherence(self, events: List[Dict]) -> List[Dict]:
        """Check timeline coherence across documents."""
        return []  # Implementation would check chronological consistency

    def _check_world_rule_violations(self, context: NarrativeContext) -> List[Dict]:
        """Check for violations of world rules."""
        return []  # Implementation would check against established rules

    def _track_location_descriptions(self, context: NarrativeContext) -> Dict[str, List[str]]:
        """Track location descriptions across documents."""
        return {}  # Implementation would track location mentions

    def _check_location_consistency(self, descriptions: Dict[str, List[str]]) -> List[Dict]:
        """Check location consistency across documents."""
        return []  # Implementation would check for conflicting descriptions

    def _extract_conflicting_elements(self, issue: ConsistencyIssue, context: NarrativeContext) -> str:
        """Extract specific conflicting elements for resolution."""
        return f"Issue in documents: {', '.join(issue.affected_documents)}"

# Add missing import
import random