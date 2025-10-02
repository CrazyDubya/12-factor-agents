"""
Evaluation utilities for the V2 Context Selection System.
"""

import numpy as np
from typing import List, Dict, Tuple, Any
from sklearn.metrics import precision_score, recall_score, f1_score

from .models import TextSegment, SelectionResult


class Evaluator:
    """Evaluates context selection performance.

    Provides metrics for evaluating the quality of segment selection
    against ground truth annotations.

    Attributes:
        baseline_selectors: Dictionary of baseline selector functions
    """

    def __init__(self):
        """Initialize the evaluator."""
        self.baseline_selectors = {
            'random': self._random_baseline,
            'first': self._first_baseline,
            'last': self._last_baseline,
            'keyword': self._keyword_baseline
        }

    def evaluate_selection(self, result: SelectionResult, ground_truth: List[int],
                          total_segments: int) -> Dict[str, float]:
        """Evaluate a single selection result.

        Args:
            result: Selection result to evaluate
            ground_truth: List of ground truth segment indices
            total_segments: Total number of segments available

        Returns:
            Dictionary with evaluation metrics
        """
        selected_indices = self._get_selected_indices(result.selected_segments, total_segments)

        precision, recall, f1 = self._calculate_metrics(
            selected_indices, ground_truth, total_segments
        )

        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'selected_count': len(selected_indices),
            'ground_truth_count': len(ground_truth),
            'method': result.method,
            'execution_time_ms': result.execution_time_ms,
            'confidence_score': result.confidence_score
        }

    def evaluate_selector(self, selector_func, query: str, segments: List[TextSegment],
                         ground_truth: List[int], budget: int) -> Dict[str, float]:
        """Evaluate a selector function.

        Args:
            selector_func: Function that selects segments
            query: Query string
            segments: List of segments to search
            ground_truth: Ground truth segment indices
            budget: Token budget

        Returns:
            Dictionary with evaluation metrics
        """
        result = selector_func(query, segments, budget)
        return self.evaluate_selection(result, ground_truth, len(segments))

    def run_evaluation_suite(self, test_data: List[Dict[str, Any]],
                            selector_func) -> Dict[str, Any]:
        """Run comprehensive evaluation on test data.

        Args:
            test_data: List of test examples with queries, segments, and ground truth
            selector_func: Function to evaluate

        Returns:
            Dictionary with comprehensive evaluation results
        """
        results = []

        for example in test_data:
            try:
                metrics = self.evaluate_selector(
                    selector_func,
                    example['query'],
                    example['segments'],
                    example['ground_truth'],
                    example.get('budget', 1000)
                )
                results.append(metrics)
            except Exception as e:
                print(f"❌ Error evaluating example: {e}")
                continue

        if not results:
            return {'error': 'No successful evaluations'}

        # Aggregate metrics
        metrics = ['precision', 'recall', 'f1_score', 'execution_time_ms']
        aggregated = {}

        for metric in metrics:
            values = [r[metric] for r in results if metric in r]
            if values:
                aggregated[metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'median': np.median(values)
                }

        aggregated['total_examples'] = len(results)
        aggregated['success_rate'] = len(results) / len(test_data)

        return aggregated

    def compare_selectors(self, test_data: List[Dict[str, Any]],
                         selectors: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple selector functions.

        Args:
            test_data: Test examples
            selectors: Dictionary of selector_name -> selector_function

        Returns:
            Comparison results
        """
        comparison = {}

        for name, selector_func in selectors.items():
            print(f"Evaluating {name}...")
            results = self.run_evaluation_suite(test_data, selector_func)
            comparison[name] = results

        return comparison

    def _get_selected_indices(self, selected_segments: List[TextSegment],
                             total_segments: int) -> List[int]:
        """Get segment indices from selected segments.

        Args:
            selected_segments: List of selected segments
            total_segments: Total number of segments

        Returns:
            List of selected segment indices
        """
        # This is a simplified implementation
        # In practice, you'd need to map segments back to original indices
        return list(range(len(selected_segments)))

    def _calculate_metrics(self, selected_indices: List[int], ground_truth: List[int],
                          total_segments: int) -> Tuple[float, float, float]:
        """Calculate precision, recall, and F1 score.

        Args:
            selected_indices: Indices of selected segments
            ground_truth: Ground truth indices
            total_segments: Total number of segments

        Returns:
            Tuple of (precision, recall, f1_score)
        """
        if not selected_indices and not ground_truth:
            return 1.0, 1.0, 1.0  # Perfect match for empty sets

        if not selected_indices:
            return 0.0, 0.0, 0.0  # No selections

        if not ground_truth:
            return 0.0, 0.0, 0.0  # No ground truth

        # Convert to binary arrays for sklearn metrics
        y_true = [1 if i in ground_truth else 0 for i in range(total_segments)]
        y_pred = [1 if i in selected_indices else 0 for i in range(total_segments)]

        try:
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
        except Exception:
            precision = recall = f1 = 0.0

        return precision, recall, f1

    def _random_baseline(self, query: str, segments: List[TextSegment], budget: int) -> SelectionResult:
        """Random selection baseline."""
        import random
        random.shuffle(segments)
        selected = []
        total_tokens = 0

        for segment in segments:
            tokens = len(segment.text.split())
            if total_tokens + tokens <= budget:
                selected.append(segment)
                total_tokens += tokens
            else:
                break

        return SelectionResult(
            selected_segments=selected,
            method="random_baseline",
            execution_time_ms=1.0,
            query=query,
            total_segments_available=len(segments),
            budget_used=total_tokens
        )

    def _first_baseline(self, query: str, segments: List[TextSegment], budget: int) -> SelectionResult:
        """First-N selection baseline."""
        selected = []
        total_tokens = 0

        for segment in segments:
            tokens = len(segment.text.split())
            if total_tokens + tokens <= budget:
                selected.append(segment)
                total_tokens += tokens
            else:
                break

        return SelectionResult(
            selected_segments=selected,
            method="first_baseline",
            execution_time_ms=0.5,
            query=query,
            total_segments_available=len(segments),
            budget_used=total_tokens
        )

    def _last_baseline(self, query: str, segments: List[TextSegment], budget: int) -> SelectionResult:
        """Last-N selection baseline."""
        selected = []
        total_tokens = 0

        for segment in reversed(segments):
            tokens = len(segment.text.split())
            if total_tokens + tokens <= budget:
                selected.insert(0, segment)  # Insert at beginning to maintain order
                total_tokens += tokens
            else:
                break

        return SelectionResult(
            selected_segments=selected,
            method="last_baseline",
            execution_time_ms=0.5,
            query=query,
            total_segments_available=len(segments),
            budget_used=total_tokens
        )

    def _keyword_baseline(self, query: str, segments: List[TextSegment], budget: int) -> SelectionResult:
        """Keyword matching baseline."""
        query_words = set(query.lower().split())
        scored_segments = []

        for segment in segments:
            segment_words = set(segment.text.lower().split())
            overlap = len(query_words & segment_words)
            scored_segments.append((overlap, segment))

        # Sort by keyword overlap
        scored_segments.sort(key=lambda x: x[0], reverse=True)

        selected = []
        total_tokens = 0

        for score, segment in scored_segments:
            if score > 0:  # Only select segments with keyword matches
                tokens = len(segment.text.split())
                if total_tokens + tokens <= budget:
                    selected.append(segment)
                    total_tokens += tokens
                else:
                    break

        return SelectionResult(
            selected_segments=selected,
            method="keyword_baseline",
            execution_time_ms=5.0,
            query=query,
            total_segments_available=len(segments),
            budget_used=total_tokens
        )