"""
Priority API integration system for real-time data collection from Congress.gov, NYS Legislature, and NYC Council.
Orchestrates data collection across federal, state, and municipal levels.
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import aiohttp
import structlog
from dataclasses import dataclass
from enum import Enum

from config.settings import settings
from apis.congress_api import CongressAPI
from apis.ny_state_api import NYStateAPI, NYCDataCollector
from models.database import get_db_session
from models.official import Official, Statement, Vote, Achievement
from data.staten_island_officials import STATEN_ISLAND_OFFICIALS

logger = structlog.get_logger()


class DataPriority(Enum):
    """Priority levels for data collection."""
    CRITICAL = "critical"  # Real-time updates needed
    HIGH = "high"  # Daily updates
    MEDIUM = "medium"  # Weekly updates
    LOW = "low"  # Monthly updates


class DataSource(Enum):
    """Available data sources."""
    CONGRESS_API = "congress_api"
    NYS_LEGISLATURE = "nys_legislature"
    NYC_COUNCIL = "nyc_council"
    FEC_API = "fec_api"
    TWITTER_API = "twitter_api"


@dataclass
class DataCollectionTask:
    """Individual data collection task."""
    source: DataSource
    official: str
    data_type: str
    priority: DataPriority
    last_updated: datetime
    next_update: datetime
    collection_frequency: timedelta
    api_client: Any


@dataclass
class CollectionResult:
    """Result of a data collection operation."""
    source: DataSource
    official: str
    data_type: str
    success: bool
    records_collected: int
    errors: List[str]
    execution_time: float
    timestamp: datetime


class PriorityAPIIntegrator:
    """Coordinates data collection across multiple API sources with priority-based scheduling."""

    def __init__(self):
        self.congress_api = None
        self.ny_state_api = None
        self.nyc_data_collector = None
        self.collection_tasks = {}
        self.collection_results = []
        self.active_sessions = {}

    async def initialize_apis(self):
        """Initialize all API clients."""
        try:
            self.congress_api = CongressAPI()
            self.ny_state_api = NYStateAPI()
            self.nyc_data_collector = NYCDataCollector()

            logger.info("API clients initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize API clients", error=str(e))
            raise

    async def shutdown_apis(self):
        """Properly shutdown all API clients."""
        if self.ny_state_api:
            await self.ny_state_api.__aexit__(None, None, None)
        if self.nyc_data_collector:
            await self.nyc_data_collector.__aexit__(None, None, None)

    def create_collection_schedule(self) -> Dict[str, List[DataCollectionTask]]:
        """Create optimized collection schedule for all Staten Island officials."""
        schedule = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        for official_name, official_data in STATEN_ISLAND_OFFICIALS.items():
            position_type = official_data.get("position_type", "")
            jurisdiction = self._get_jurisdiction_from_position(position_type)

            # Create tasks based on jurisdiction and position importance
            tasks = self._create_tasks_for_official(official_name, jurisdiction, position_type)
            for task in tasks:
                schedule[task.priority.value].append(task)

        return schedule

    def _get_jurisdiction_from_position(self, position_type: str) -> str:
        """Determine jurisdiction from position type."""
        position_lower = position_type.lower()
        if "senator" in position_lower and "state" not in position_lower:
            return "federal"
        elif "representative" in position_lower or "congress" in position_lower:
            return "federal"
        elif "state" in position_lower or "assembly" in position_lower:
            return "state"
        elif "council" in position_lower or "borough" in position_lower or "mayor" in position_lower:
            return "municipal"
        else:
            return "unknown"

    def _create_tasks_for_official(self, official_name: str, jurisdiction: str,
                                 position_type: str) -> List[DataCollectionTask]:
        """Create data collection tasks for a specific official."""
        tasks = []
        now = datetime.now()

        if jurisdiction == "federal":
            # Congress.gov API tasks
            tasks.extend([
                DataCollectionTask(
                    source=DataSource.CONGRESS_API,
                    official=official_name,
                    data_type="votes",
                    priority=DataPriority.HIGH,
                    last_updated=now - timedelta(days=1),
                    next_update=now,
                    collection_frequency=timedelta(days=1),
                    api_client=self.congress_api
                ),
                DataCollectionTask(
                    source=DataSource.CONGRESS_API,
                    official=official_name,
                    data_type="bills_sponsored",
                    priority=DataPriority.HIGH,
                    last_updated=now - timedelta(days=1),
                    next_update=now,
                    collection_frequency=timedelta(days=1),
                    api_client=self.congress_api
                ),
                DataCollectionTask(
                    source=DataSource.CONGRESS_API,
                    official=official_name,
                    data_type="statements",
                    priority=DataPriority.MEDIUM,
                    last_updated=now - timedelta(days=7),
                    next_update=now,
                    collection_frequency=timedelta(days=7),
                    api_client=self.congress_api
                ),
                DataCollectionTask(
                    source=DataSource.FEC_API,
                    official=official_name,
                    data_type="campaign_finance",
                    priority=DataPriority.LOW,
                    last_updated=now - timedelta(days=30),
                    next_update=now,
                    collection_frequency=timedelta(days=30),
                    api_client=self.congress_api
                )
            ])

        elif jurisdiction == "state":
            # NYS Legislature API tasks
            tasks.extend([
                DataCollectionTask(
                    source=DataSource.NYS_LEGISLATURE,
                    official=official_name,
                    data_type="votes",
                    priority=DataPriority.HIGH,
                    last_updated=now - timedelta(days=1),
                    next_update=now,
                    collection_frequency=timedelta(days=1),
                    api_client=self.ny_state_api
                ),
                DataCollectionTask(
                    source=DataSource.NYS_LEGISLATURE,
                    official=official_name,
                    data_type="sponsored_bills",
                    priority=DataPriority.HIGH,
                    last_updated=now - timedelta(days=1),
                    next_update=now,
                    collection_frequency=timedelta(days=1),
                    api_client=self.ny_state_api
                ),
                DataCollectionTask(
                    source=DataSource.NYS_LEGISLATURE,
                    official=official_name,
                    data_type="member_details",
                    priority=DataPriority.MEDIUM,
                    last_updated=now - timedelta(days=7),
                    next_update=now,
                    collection_frequency=timedelta(days=7),
                    api_client=self.ny_state_api
                )
            ])

        elif jurisdiction == "municipal":
            # NYC Council/Municipal API tasks
            tasks.extend([
                DataCollectionTask(
                    source=DataSource.NYC_COUNCIL,
                    official=official_name,
                    data_type="council_votes",
                    priority=DataPriority.MEDIUM,
                    last_updated=now - timedelta(days=7),
                    next_update=now,
                    collection_frequency=timedelta(days=7),
                    api_client=self.nyc_data_collector
                ),
                DataCollectionTask(
                    source=DataSource.NYC_COUNCIL,
                    official=official_name,
                    data_type="member_info",
                    priority=DataPriority.LOW,
                    last_updated=now - timedelta(days=30),
                    next_update=now,
                    collection_frequency=timedelta(days=30),
                    api_client=self.nyc_data_collector
                )
            ])

        # Add social media monitoring for all officials
        tasks.append(DataCollectionTask(
            source=DataSource.TWITTER_API,
            official=official_name,
            data_type="tweets",
            priority=DataPriority.MEDIUM,
            last_updated=now - timedelta(days=7),
            next_update=now,
            collection_frequency=timedelta(days=7),
            api_client=None  # Would need Twitter API client
        ))

        return tasks

    async def execute_priority_collection(self, priority: DataPriority,
                                        max_concurrent: int = 5) -> List[CollectionResult]:
        """Execute data collection for a specific priority level."""
        schedule = self.create_collection_schedule()
        tasks = schedule.get(priority.value, [])

        # Filter tasks that need updating
        due_tasks = [task for task in tasks if task.next_update <= datetime.now()]

        if not due_tasks:
            logger.info("No tasks due for priority level", priority=priority.value)
            return []

        logger.info("Executing priority collection", priority=priority.value, task_count=len(due_tasks))

        # Execute tasks with concurrency limit
        semaphore = asyncio.Semaphore(max_concurrent)
        collection_coroutines = [
            self._execute_single_task(task, semaphore) for task in due_tasks
        ]

        results = await asyncio.gather(*collection_coroutines, return_exceptions=True)

        # Process results
        collection_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                collection_results.append(CollectionResult(
                    source=due_tasks[i].source,
                    official=due_tasks[i].official,
                    data_type=due_tasks[i].data_type,
                    success=False,
                    records_collected=0,
                    errors=[str(result)],
                    execution_time=0.0,
                    timestamp=datetime.now()
                ))
            else:
                collection_results.append(result)

        self.collection_results.extend(collection_results)
        return collection_results

    async def _execute_single_task(self, task: DataCollectionTask,
                                 semaphore: asyncio.Semaphore) -> CollectionResult:
        """Execute a single data collection task."""
        async with semaphore:
            start_time = datetime.now()
            try:
                result = await self._collect_data_for_task(task)
                execution_time = (datetime.now() - start_time).total_seconds()

                return CollectionResult(
                    source=task.source,
                    official=task.official,
                    data_type=task.data_type,
                    success=True,
                    records_collected=result.get("record_count", 0),
                    errors=[],
                    execution_time=execution_time,
                    timestamp=datetime.now()
                )

            except Exception as e:
                execution_time = (datetime.now() - start_time).total_seconds()
                logger.error("Task execution failed", task=task.data_type, official=task.official, error=str(e))

                return CollectionResult(
                    source=task.source,
                    official=task.official,
                    data_type=task.data_type,
                    success=False,
                    records_collected=0,
                    errors=[str(e)],
                    execution_time=execution_time,
                    timestamp=datetime.now()
                )

    async def _collect_data_for_task(self, task: DataCollectionTask) -> Dict[str, Any]:
        """Collect data for a specific task."""
        official_data = STATEN_ISLAND_OFFICIALS.get(task.official, {})

        if task.source == DataSource.CONGRESS_API:
            return await self._collect_congress_data(task, official_data)
        elif task.source == DataSource.NYS_LEGISLATURE:
            return await self._collect_nys_data(task, official_data)
        elif task.source == DataSource.NYC_COUNCIL:
            return await self._collect_nyc_data(task, official_data)
        elif task.source == DataSource.TWITTER_API:
            return await self._collect_social_media_data(task, official_data)
        else:
            raise ValueError(f"Unsupported data source: {task.source}")

    async def _collect_congress_data(self, task: DataCollectionTask, official_data: Dict) -> Dict[str, Any]:
        """Collect data from Congress.gov API."""
        if not self.congress_api:
            raise ValueError("Congress API not initialized")

        bioguide_id = official_data.get("bioguide_id")
        if not bioguide_id:
            # Try to find by name matching
            bioguide_id = await self._find_bioguide_id(task.official)

        if task.data_type == "votes":
            votes = await self.congress_api.get_member_votes(bioguide_id)
            return {"data": votes, "record_count": len(votes)}

        elif task.data_type == "bills_sponsored":
            bills = await self.congress_api.get_sponsored_bills(bioguide_id)
            return {"data": bills, "record_count": len(bills)}

        elif task.data_type == "statements":
            statements = await self.congress_api.get_member_statements(bioguide_id)
            return {"data": statements, "record_count": len(statements)}

        elif task.data_type == "campaign_finance":
            finance_data = await self.congress_api.get_campaign_finance(bioguide_id)
            return {"data": finance_data, "record_count": len(finance_data.get("contributions", []))}

        else:
            raise ValueError(f"Unsupported Congress data type: {task.data_type}")

    async def _collect_nys_data(self, task: DataCollectionTask, official_data: Dict) -> Dict[str, Any]:
        """Collect data from NYS Legislature API."""
        if not self.ny_state_api:
            raise ValueError("NYS API not initialized")

        member_id = official_data.get("nys_member_id")
        if not member_id:
            # Try to find by name/district matching
            member_id = await self._find_nys_member_id(task.official, official_data)

        session_year = datetime.now().year

        if task.data_type == "votes":
            votes = await self.ny_state_api.get_member_votes(member_id, session_year)
            return {"data": votes, "record_count": len(votes)}

        elif task.data_type == "sponsored_bills":
            bills = await self.ny_state_api.get_member_sponsored_bills(member_id, session_year)
            return {"data": bills, "record_count": len(bills)}

        elif task.data_type == "member_details":
            details = await self.ny_state_api.get_member_details(member_id, session_year)
            return {"data": details, "record_count": 1 if details else 0}

        else:
            raise ValueError(f"Unsupported NYS data type: {task.data_type}")

    async def _collect_nyc_data(self, task: DataCollectionTask, official_data: Dict) -> Dict[str, Any]:
        """Collect data from NYC Council API."""
        if not self.nyc_data_collector:
            raise ValueError("NYC data collector not initialized")

        if task.data_type == "council_votes":
            # Placeholder for NYC Council vote data
            return {"data": [], "record_count": 0}

        elif task.data_type == "member_info":
            if "council" in official_data.get("position_type", "").lower():
                members = await self.nyc_data_collector.get_council_members()
                return {"data": members, "record_count": len(members)}
            elif "borough president" in official_data.get("position_type", "").lower():
                borough_pres = await self.nyc_data_collector.get_borough_president()
                return {"data": [borough_pres], "record_count": 1}
            else:
                return {"data": [], "record_count": 0}

        else:
            raise ValueError(f"Unsupported NYC data type: {task.data_type}")

    async def _collect_social_media_data(self, task: DataCollectionTask, official_data: Dict) -> Dict[str, Any]:
        """Collect social media data (placeholder for Twitter API)."""
        # This would require Twitter API integration
        logger.info("Social media collection not implemented", official=task.official)
        return {"data": [], "record_count": 0}

    async def _find_bioguide_id(self, official_name: str) -> Optional[str]:
        """Find bioguide ID for an official by name."""
        # This would implement name matching logic with Congress API
        name_mapping = {
            "Charles Schumer": "S000148",
            "Kirsten Gillibrand": "G000555",
            "Nicole Malliotakis": "M001207"
        }
        return name_mapping.get(official_name)

    async def _find_nys_member_id(self, official_name: str, official_data: Dict) -> Optional[str]:
        """Find NYS member ID for an official."""
        # This would implement district-based lookup
        if "Andrew Lanza" in official_name:
            return "lanza"  # Placeholder
        return None

    async def run_full_collection_cycle(self) -> Dict[str, Any]:
        """Run a complete collection cycle for all priority levels."""
        await self.initialize_apis()

        try:
            cycle_results = {}
            total_records = 0
            total_errors = 0

            # Execute in priority order
            for priority in [DataPriority.CRITICAL, DataPriority.HIGH, DataPriority.MEDIUM, DataPriority.LOW]:
                results = await self.execute_priority_collection(priority)
                cycle_results[priority.value] = results

                total_records += sum(r.records_collected for r in results)
                total_errors += sum(len(r.errors) for r in results)

                # Brief pause between priority levels
                await asyncio.sleep(1)

            return {
                "cycle_summary": {
                    "total_tasks_executed": sum(len(results) for results in cycle_results.values()),
                    "total_records_collected": total_records,
                    "total_errors": total_errors,
                    "execution_time": datetime.now().isoformat()
                },
                "results_by_priority": cycle_results
            }

        finally:
            await self.shutdown_apis()

    def get_collection_statistics(self) -> Dict[str, Any]:
        """Get statistics about recent collection activities."""
        if not self.collection_results:
            return {"message": "No collection results available"}

        recent_results = [r for r in self.collection_results
                         if (datetime.now() - r.timestamp).days <= 7]

        success_rate = sum(1 for r in recent_results if r.success) / len(recent_results) if recent_results else 0
        avg_execution_time = sum(r.execution_time for r in recent_results) / len(recent_results) if recent_results else 0

        results_by_source = {}
        for result in recent_results:
            source = result.source.value
            if source not in results_by_source:
                results_by_source[source] = {"success": 0, "failure": 0, "records": 0}

            if result.success:
                results_by_source[source]["success"] += 1
                results_by_source[source]["records"] += result.records_collected
            else:
                results_by_source[source]["failure"] += 1

        return {
            "recent_activity": {
                "total_collections": len(recent_results),
                "success_rate": success_rate,
                "average_execution_time": avg_execution_time,
                "total_records_collected": sum(r.records_collected for r in recent_results)
            },
            "by_source": results_by_source,
            "most_active_officials": self._get_most_collected_officials(recent_results)
        }

    def _get_most_collected_officials(self, results: List[CollectionResult]) -> List[Tuple[str, int]]:
        """Get officials with most collection activity."""
        official_counts = {}
        for result in results:
            official_counts[result.official] = official_counts.get(result.official, 0) + 1

        return sorted(official_counts.items(), key=lambda x: x[1], reverse=True)[:5]