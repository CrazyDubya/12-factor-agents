"""
Async task queue system for background data collection and processing.
"""
import asyncio
from celery import Celery
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
from config.settings import settings
from apis.congress_api import CongressAPI
from apis.fec_api import FECAPI
from apis.social_media_api import SocialMediaCollector
from collectors.web_scraper import GovernmentScraper, CSpanScraper
from processors.transcript_processor import TranscriptProcessor

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery(
    'official_profiler',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


class AsyncDataCollector:
    """Manages async data collection tasks."""

    def __init__(self):
        self.congress_api = None
        self.fec_api = None
        self.social_collector = None
        self.web_scraper = None
        self.cspan_scraper = None
        self.transcript_processor = None

    async def initialize(self):
        """Initialize API clients and services."""
        self.congress_api = CongressAPI()
        self.fec_api = FECAPI()
        self.social_collector = SocialMediaCollector()
        self.web_scraper = GovernmentScraper()
        self.cspan_scraper = CSpanScraper()
        self.transcript_processor = TranscriptProcessor()

    async def cleanup(self):
        """Cleanup resources."""
        if self.congress_api:
            await self.congress_api.__aexit__(None, None, None)
        if self.fec_api:
            await self.fec_api.__aexit__(None, None, None)


# Celery Tasks
@celery_app.task(bind=True)
def collect_congressional_data(self, bioguide_id: str, congress: int = 118):
    """Collect comprehensive congressional data for an official."""
    return asyncio.run(_collect_congressional_data_async(bioguide_id, congress))


async def _collect_congressional_data_async(bioguide_id: str, congress: int):
    """Async implementation of congressional data collection."""
    collector = AsyncDataCollector()
    await collector.initialize()

    try:
        data_package = {
            "bioguide_id": bioguide_id,
            "congress": congress,
            "collected_at": datetime.now().isoformat(),
            "member_details": {},
            "voting_record": [],
            "sponsored_legislation": [],
            "committee_assignments": []
        }

        async with collector.congress_api as api:
            # Get member details
            member_details = await api.get_member_details(bioguide_id)
            data_package["member_details"] = member_details

            # Get voting record
            votes = await api.get_member_votes(bioguide_id, congress, limit=500)
            data_package["voting_record"] = votes

            # Get sponsored legislation
            legislation = await api.get_member_sponsored_legislation(bioguide_id, congress)
            data_package["sponsored_legislation"] = legislation

        logger.info("Congressional data collected", bioguide_id=bioguide_id,
                   votes=len(data_package["voting_record"]),
                   bills=len(data_package["sponsored_legislation"]))

        return data_package

    except Exception as e:
        logger.error("Congressional data collection failed",
                    bioguide_id=bioguide_id, error=str(e))
        raise
    finally:
        await collector.cleanup()


@celery_app.task(bind=True)
def collect_financial_data(self, candidate_name: str, fec_id: str = None):
    """Collect campaign finance and FEC data."""
    return asyncio.run(_collect_financial_data_async(candidate_name, fec_id))


async def _collect_financial_data_async(candidate_name: str, fec_id: str = None):
    """Async implementation of financial data collection."""
    collector = AsyncDataCollector()
    await collector.initialize()

    try:
        financial_package = {
            "candidate_name": candidate_name,
            "fec_id": fec_id,
            "collected_at": datetime.now().isoformat(),
            "candidate_info": {},
            "financial_summary": {},
            "major_contributors": [],
            "expenditures": []
        }

        async with collector.fec_api as api:
            # Search for candidate if no FEC ID provided
            if not fec_id:
                candidates = await api.search_candidates(candidate_name)
                if candidates:
                    fec_id = candidates[0]["candidate_id"]
                    financial_package["fec_id"] = fec_id

            if fec_id:
                # Get candidate info
                candidate_info = await api.get_candidate_info(fec_id)
                financial_package["candidate_info"] = candidate_info

                # Get comprehensive financial summary
                financial_summary = await api.get_financial_summary(fec_id)
                financial_package["financial_summary"] = financial_summary

        logger.info("Financial data collected", candidate_name=candidate_name,
                   fec_id=fec_id)

        return financial_package

    except Exception as e:
        logger.error("Financial data collection failed",
                    candidate_name=candidate_name, error=str(e))
        raise
    finally:
        await collector.cleanup()


@celery_app.task(bind=True)
def collect_social_media_data(self, official_data: Dict):
    """Collect social media data for an official."""
    return asyncio.run(_collect_social_media_data_async(official_data))


async def _collect_social_media_data_async(official_data: Dict):
    """Async implementation of social media collection."""
    collector = AsyncDataCollector()
    await collector.initialize()

    try:
        social_package = await collector.social_collector.collect_official_social_data(
            official_data
        )

        logger.info("Social media data collected",
                   official=official_data.get("full_name"),
                   twitter_tweets=len(social_package.get("twitter", {}).get("recent_tweets", [])),
                   facebook_posts=len(social_package.get("facebook", {}).get("recent_posts", [])))

        return social_package

    except Exception as e:
        logger.error("Social media collection failed",
                    official=official_data.get("full_name"), error=str(e))
        raise
    finally:
        await collector.cleanup()


@celery_app.task(bind=True)
def scrape_government_sites(self, official_data: Dict):
    """Scrape government websites for additional data."""
    return asyncio.run(_scrape_government_sites_async(official_data))


async def _scrape_government_sites_async(official_data: Dict):
    """Async implementation of government site scraping."""
    collector = AsyncDataCollector()
    await collector.initialize()

    try:
        scraping_package = {
            "official": official_data,
            "collected_at": datetime.now().isoformat(),
            "biography_data": {},
            "press_releases": [],
            "cspan_appearances": []
        }

        bioguide_id = official_data.get("bioguide_id")
        chamber = "house" if "representative" in official_data.get("position_type", "").lower() else "senate"

        # Scrape biography page
        if bioguide_id:
            bio_data = await collector.web_scraper.scrape_member_bio_page(
                bioguide_id, chamber
            )
            scraping_package["biography_data"] = bio_data

        # Search C-SPAN appearances
        full_name = official_data.get("full_name")
        if full_name:
            cspan_appearances = await collector.cspan_scraper.search_cspan_appearances(
                full_name, days_back=90
            )
            scraping_package["cspan_appearances"] = cspan_appearances

        logger.info("Government site scraping completed",
                   official=full_name,
                   cspan_appearances=len(scraping_package["cspan_appearances"]))

        return scraping_package

    except Exception as e:
        logger.error("Government site scraping failed",
                    official=official_data.get("full_name"), error=str(e))
        raise
    finally:
        await collector.cleanup()


@celery_app.task(bind=True)
def process_transcript(self, transcript_data: Dict):
    """Process transcript for NLP analysis."""
    return asyncio.run(_process_transcript_async(transcript_data))


async def _process_transcript_async(transcript_data: Dict):
    """Async implementation of transcript processing."""
    collector = AsyncDataCollector()
    await collector.initialize()

    try:
        if "audio_path" in transcript_data:
            # Transcribe audio first
            transcription = await collector.transcript_processor.transcribe_audio(
                transcript_data["audio_path"]
            )
            transcript_text = transcription.get("text", "")
        else:
            transcript_text = transcript_data.get("text", "")

        if not transcript_text:
            return {"error": "No transcript text available"}

        # Process transcript
        analysis = await collector.transcript_processor.process_transcript(
            transcript_text,
            speaker_info=transcript_data.get("speaker_info")
        )

        # Process speaker identification if segments available
        if "segments" in transcript_data:
            speaker_analysis = await collector.transcript_processor.process_speaker_identification(
                transcript_data["segments"]
            )
            analysis["speaker_analysis"] = speaker_analysis

        logger.info("Transcript processed",
                   word_count=analysis.get("word_count", 0),
                   entities_found=len(analysis.get("entities", {})),
                   topics_found=len(analysis.get("topics", [])))

        return analysis

    except Exception as e:
        logger.error("Transcript processing failed", error=str(e))
        raise
    finally:
        await collector.cleanup()


@celery_app.task(bind=True)
def update_official_profile(self, official_id: str):
    """Comprehensive update of an official's profile."""
    return asyncio.run(_update_official_profile_async(official_id))


async def _update_official_profile_async(official_id: str):
    """Async implementation of profile update."""
    # This would orchestrate multiple data collection tasks
    update_results = {
        "official_id": official_id,
        "update_started": datetime.now().isoformat(),
        "tasks_completed": [],
        "tasks_failed": [],
        "overall_status": "running"
    }

    try:
        # Kick off parallel collection tasks
        from models.database import get_db
        from models.official import Official

        # Get official data from database
        # This is a simplified version - in practice would use proper session management
        db = next(get_db())
        official = db.query(Official).filter_by(id=official_id).first()

        if not official:
            update_results["overall_status"] = "failed"
            update_results["error"] = "Official not found"
            return update_results

        official_data = {
            "id": str(official.id),
            "bioguide_id": official.bioguide_id,
            "full_name": official.full_name,
            "twitter_handle": official.twitter_handle,
            "facebook_url": official.facebook_url
        }

        # Launch collection tasks
        tasks = []

        # Congressional data
        if official.bioguide_id:
            congressional_task = collect_congressional_data.delay(
                official.bioguide_id
            )
            tasks.append(("congressional", congressional_task))

        # Financial data
        financial_task = collect_financial_data.delay(
            official.full_name
        )
        tasks.append(("financial", financial_task))

        # Social media data
        social_task = collect_social_media_data.delay(official_data)
        tasks.append(("social_media", social_task))

        # Government site scraping
        scraping_task = scrape_government_sites.delay(official_data)
        tasks.append(("government_scraping", scraping_task))

        # Wait for tasks to complete
        for task_name, task in tasks:
            try:
                result = task.get(timeout=300)  # 5 minute timeout per task
                update_results["tasks_completed"].append({
                    "task": task_name,
                    "status": "success",
                    "completed_at": datetime.now().isoformat()
                })
                logger.info("Task completed", task=task_name, official_id=official_id)
            except Exception as e:
                update_results["tasks_failed"].append({
                    "task": task_name,
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                })
                logger.error("Task failed", task=task_name, official_id=official_id, error=str(e))

        # Determine overall status
        if update_results["tasks_failed"]:
            if update_results["tasks_completed"]:
                update_results["overall_status"] = "partial_success"
            else:
                update_results["overall_status"] = "failed"
        else:
            update_results["overall_status"] = "success"

        update_results["update_completed"] = datetime.now().isoformat()

        return update_results

    except Exception as e:
        update_results["overall_status"] = "failed"
        update_results["error"] = str(e)
        update_results["update_completed"] = datetime.now().isoformat()
        logger.error("Profile update failed", official_id=official_id, error=str(e))
        return update_results


# Periodic Tasks
@celery_app.task
def daily_profile_updates():
    """Daily task to update all active official profiles."""
    from models.database import get_db
    from models.official import Official

    db = next(get_db())
    active_officials = db.query(Official).filter(
        Official.currently_serving == True
    ).all()

    update_tasks = []
    for official in active_officials:
        # Check if profile needs updating (based on last update time)
        if official.last_profile_update:
            days_since_update = (datetime.now() - official.last_profile_update).days
            if days_since_update < settings.UPDATE_FREQUENCY_HOURS / 24:
                continue  # Skip if recently updated

        # Launch update task
        task = update_official_profile.delay(str(official.id))
        update_tasks.append(task)

        # Limit concurrent updates
        if len(update_tasks) >= settings.MAX_CONCURRENT_REQUESTS:
            break

    logger.info("Daily profile updates initiated", count=len(update_tasks))
    return {"initiated_updates": len(update_tasks)}


# Task monitoring utilities
class TaskMonitor:
    """Monitor and manage async tasks."""

    @staticmethod
    def get_task_status(task_id: str) -> Dict:
        """Get status of a specific task."""
        task = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.successful() else None,
            "error": str(task.result) if task.failed() else None,
            "traceback": task.traceback if task.failed() else None
        }

    @staticmethod
    def get_active_tasks() -> List[Dict]:
        """Get list of all active tasks."""
        active_tasks = celery_app.control.inspect().active()
        if not active_tasks:
            return []

        all_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                all_tasks.append({
                    "worker": worker,
                    "task_id": task["id"],
                    "name": task["name"],
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {}),
                    "time_start": task.get("time_start")
                })

        return all_tasks

    @staticmethod
    def cancel_task(task_id: str) -> bool:
        """Cancel a running task."""
        celery_app.control.revoke(task_id, terminate=True)
        return True

    @staticmethod
    def get_queue_status() -> Dict:
        """Get status of task queues."""
        stats = celery_app.control.inspect().stats()
        return stats or {}


# Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'daily-profile-updates': {
        'task': 'utils.async_tasks.daily_profile_updates',
        'schedule': 86400.0,  # 24 hours
    },
}
celery_app.conf.timezone = 'UTC'