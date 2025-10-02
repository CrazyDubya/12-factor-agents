"""
Performance benchmarks for the V2 Context Selection System.
"""

import time
import statistics
import numpy as np
from v2_context_selector.tests import TextSegment, ContextSelector, Config, fast_config, balanced_config, accurate_config


class PerformanceBenchmarks:
    """Comprehensive performance benchmarks."""

    def setup_method(self):
        """Set up benchmark fixtures."""
        self.queries = [
            "What is artificial intelligence?",
            "How do machine learning algorithms work?",
            "Explain neural networks and deep learning",
            "What are the latest developments in computer vision?",
            "How do computers process visual information?",
            "Describe natural language processing",
            "What is data science and analytics?",
            "Explain algorithmic complexity",
            "How do databases store information?",
            "What are the principles of software engineering?"
        ]

    def create_test_segments(self, count=100):
        """Create test segments with realistic content."""
        segments = []
        topics = [
            "artificial intelligence and machine learning",
            "neural networks and deep learning algorithms",
            "computer vision and image processing",
            "natural language processing and text analysis",
            "data science and statistical analysis",
            "software engineering and development",
            "database systems and information storage",
            "algorithmic complexity and optimization",
            "computer architecture and systems",
            "cybersecurity and network protocols"
        ]

        for i in range(count):
            topic = topics[i % len(topics)]
            text = f"This segment discusses {topic}. "
            text += f"It contains relevant information about {topic} "
            text += f"with technical details and examples. Segment {i} "
            text += f"provides comprehensive coverage of {topic} concepts."

            segments.append(TextSegment(
                id=f"seg_{i}",
                text=text,
                document_id=f"doc_{i // 10}",
                position=i
            ))

        return segments

    def benchmark_configuration(self, config, name, segment_count=100):
        """Benchmark a specific configuration."""
        print(f"\n🚀 Benchmarking {name} Configuration")
        print(f"   Segments: {segment_count}")
        print(f"   Queries: {len(self.queries)}")

        selector = ContextSelector(config)
        segments = self.create_test_segments(segment_count)

        # Warm up
        selector.preload_documents(segments)

        # Run benchmarks
        times = []
        selection_counts = []
        confidence_scores = []

        for i, query in enumerate(self.queries):
            start_time = time.time()
            result = selector.select(query, segments, budget=1000)
            end_time = time.time()

            execution_time = (end_time - start_time) * 1000
            times.append(execution_time)
            selection_counts.append(len(result.selected_segments))
            confidence_scores.append(result.confidence_score)

            if i < 3:  # Show first few results
                print(f"   Query {i+1}: {execution_time:.1f}ms, {len(result.selected_segments)} segments")

        # Calculate statistics
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        p95_time = np.percentile(times, 95)
        min_time = min(times)
        max_time = max(times)

        avg_selections = statistics.mean(selection_counts)
        avg_confidence = statistics.mean(confidence_scores)

        # Get cache stats
        cache_stats = selector.get_performance_stats()['cache_stats']

        print(f"   📊 Results:")
        print(f"      Average time: {avg_time:.1f}ms")
        print(f"      Median time: {median_time:.1f}ms")
        print(f"      95th percentile: {p95_time:.1f}ms")
        print(f"      Range: {min_time:.1f}ms - {max_time:.1f}ms")
        print(f"      Avg selections: {avg_selections:.1f}")
        print(f"      Avg confidence: {avg_confidence:.3f}")
        print(f"      Cache hit rate: {cache_stats['hit_rate']:.1%}")

        return {
            'name': name,
            'segment_count': segment_count,
            'avg_time': avg_time,
            'median_time': median_time,
            'p95_time': p95_time,
            'min_time': min_time,
            'max_time': max_time,
            'avg_selections': avg_selections,
            'avg_confidence': avg_confidence,
            'cache_hit_rate': cache_stats['hit_rate'],
            'times': times
        }

    def benchmark_scalability(self):
        """Test scalability with different segment counts."""
        print(f"\n📈 Scalability Benchmark")

        results = {}
        segment_counts = [10, 50, 100, 500, 1000]

        for count in segment_counts:
            if count > 500:  # Skip very large tests for speed
                print(f"   Skipping {count} segments (too large for quick benchmark)")
                continue

            print(f"\n   Testing {count} segments...")
            config = balanced_config()
            result = self.benchmark_configuration(config, f"Scale_{count}", count)
            results[count] = result

        print(f"\n📊 Scalability Results:")
        print(f"   {'Segments':<10} {'Avg Time':<12} {'Cache Hit':<12}")
        print(f"   {'-'*10:<10} {'-'*12:<12} {'-'*12:<12}")

        for count, result in results.items():
            print(f"   {count:<10} {result['avg_time']:<12.1f} {result['cache_hit_rate']:<12.1%}")

        return results

    def benchmark_configurations(self):
        """Compare different configuration presets."""
        print(f"\n⚙️ Configuration Comparison Benchmark")

        configs = [
            (fast_config(), "Fast"),
            (balanced_config(), "Balanced"),
            (accurate_config(), "Accurate")
        ]

        results = []
        for config, name in configs:
            result = self.benchmark_configuration(config, name, 100)
            results.append(result)

        print(f"\n📊 Configuration Comparison:")
        print(f"   {'Config':<12} {'Avg Time':<12} {'95th Pct':<12} {'Selections':<12} {'Confidence':<12}")
        print(f"   {'-'*12:<12} {'-'*12:<12} {'-'*12:<12} {'-'*12:<12} {'-'*12:<12}")

        for result in results:
            print(f"   {result['name']:<12} {result['avg_time']:<12.1f} "
                  f"{result['p95_time']:<12.1f} {result['avg_selections']:<12.1f} "
                  f"{result['avg_confidence']:<12.3f}")

        return results

    def benchmark_cache_performance(self):
        """Test cache performance with repeated queries."""
        print(f"\n💾 Cache Performance Benchmark")

        selector = ContextSelector(balanced_config())
        segments = self.create_test_segments(100)

        # First pass (cache misses)
        print(f"   First pass (cache misses)...")
        first_times = []
        for query in self.queries[:5]:  # Use fewer queries for cache test
            start = time.time()
            selector.select(query, segments, budget=1000)
            end = time.time()
            first_times.append((end - start) * 1000)

        # Second pass (cache hits)
        print(f"   Second pass (cache hits)...")
        second_times = []
        for query in self.queries[:5]:
            start = time.time()
            selector.select(query, segments, budget=1000)
            end = time.time()
            second_times.append((end - start) * 1000)

        # Calculate improvement
        first_avg = statistics.mean(first_times)
        second_avg = statistics.mean(second_times)
        improvement = ((first_avg - second_avg) / first_avg) * 100

        cache_stats = selector.get_performance_stats()['cache_stats']

        print(f"   📊 Cache Results:")
        print(f"      First pass avg: {first_avg:.1f}ms")
        print(f"      Second pass avg: {second_avg:.1f}ms")
        print(f"      Improvement: {improvement:.1f}%")
        print(f"      Cache hit rate: {cache_stats['hit_rate']:.1%}")
        print(f"      Cache size: {cache_stats['cache_size']}")

        return {
            'first_avg': first_avg,
            'second_avg': second_avg,
            'improvement_percent': improvement,
            'cache_hit_rate': cache_stats['hit_rate']
        }

    def run_full_benchmark(self):
        """Run complete benchmark suite."""
        print(f"🏁 V2 Context Selection System - Performance Benchmarks")
        print(f"=" * 60)

        start_time = time.time()

        # Configuration comparison
        config_results = self.benchmark_configurations()

        # Scalability test
        scalability_results = self.benchmark_scalability()

        # Cache performance
        cache_results = self.benchmark_cache_performance()

        total_time = time.time() - start_time

        print(f"\n🎯 Benchmark Summary")
        print(f"   Total benchmark time: {total_time:.1f}s")
        print(f"   Configurations tested: {len(config_results)}")
        print(f"   Scalability points: {len(scalability_results)}")
        print(f"   Cache improvement: {cache_results['improvement_percent']:.1f}%")

        # Find best configuration
        best_config = min(config_results, key=lambda x: x['avg_time'])
        print(f"\n🏆 Best Performance:")
        print(f"   Configuration: {best_config['name']}")
        print(f"   Average time: {best_config['avg_time']:.1f}ms")
        print(f"   95th percentile: {best_config['p95_time']:.1f}ms")

        return {
            'config_results': config_results,
            'scalability_results': scalability_results,
            'cache_results': cache_results,
            'best_config': best_config,
            'total_time': total_time
        }


def main():
    """Run performance benchmarks."""
    benchmarks = PerformanceBenchmarks()
    results = benchmarks.run_full_benchmark()
    return results


if __name__ == "__main__":
    results = main()
    print(f"\n✅ Benchmarks completed successfully")
    print(f"   Detailed results available in returned data structure")