"""
Social media API clients for collecting public statements.
"""
import tweepy
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings
import structlog

logger = structlog.get_logger()


class TwitterAPI:
    """Twitter API v2 client for collecting tweets."""

    def __init__(self):
        if not all([settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET,
                   settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET]):
            logger.warning("Twitter API credentials not configured")
            self.client = None
            return

        self.client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )

    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user information by username."""
        if not self.client:
            return None

        try:
            user = self.client.get_user(username=username, user_fields=[
                "created_at", "description", "location", "public_metrics",
                "url", "verified"
            ])
            return user.data._json if user.data else None
        except Exception as e:
            logger.error("Error fetching Twitter user", username=username, error=str(e))
            return None

    async def get_user_tweets(self, username: str, max_results: int = 100,
                            days_back: int = 30) -> List[Dict]:
        """Get recent tweets from a user."""
        if not self.client:
            return []

        try:
            # Get user ID first
            user = await self.get_user_by_username(username)
            if not user:
                return []

            user_id = user["id"]
            start_time = datetime.now() - timedelta(days=days_back)

            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                start_time=start_time,
                tweet_fields=["created_at", "public_metrics", "context_annotations",
                            "entities", "referenced_tweets", "reply_settings"],
                exclude=["retweets", "replies"]  # Focus on original content
            )

            return [tweet._json for tweet in tweets.data] if tweets.data else []

        except Exception as e:
            logger.error("Error fetching tweets", username=username, error=str(e))
            return []

    async def search_tweets_by_user(self, username: str, query: str,
                                  max_results: int = 50) -> List[Dict]:
        """Search tweets by a specific user with query terms."""
        if not self.client:
            return []

        try:
            search_query = f"from:{username} {query}"
            tweets = self.client.search_recent_tweets(
                query=search_query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "context_annotations",
                            "entities", "referenced_tweets"]
            )

            return [tweet._json for tweet in tweets.data] if tweets.data else []

        except Exception as e:
            logger.error("Error searching tweets", username=username, query=query, error=str(e))
            return []

    async def get_tweet_details(self, tweet_id: str) -> Optional[Dict]:
        """Get detailed information about a specific tweet."""
        if not self.client:
            return None

        try:
            tweet = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=["created_at", "public_metrics", "context_annotations",
                            "entities", "referenced_tweets", "author_id"],
                expansions=["author_id", "referenced_tweets.id"]
            )
            return tweet.data._json if tweet.data else None

        except Exception as e:
            logger.error("Error fetching tweet details", tweet_id=tweet_id, error=str(e))
            return None


class FacebookAPI:
    """Facebook Graph API client (limited to public pages)."""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)
        self.base_url = "https://graph.facebook.com/v18.0"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get_page_info(self, page_id: str) -> Optional[Dict]:
        """Get basic information about a Facebook page."""
        if not self.access_token:
            return None

        url = f"{self.base_url}/{page_id}"
        params = {
            "access_token": self.access_token,
            "fields": "id,name,username,about,category,fan_count,website,link"
        }

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Error fetching Facebook page", page_id=page_id, error=str(e))
            return None

    async def get_page_posts(self, page_id: str, limit: int = 50) -> List[Dict]:
        """Get recent posts from a Facebook page."""
        if not self.access_token:
            return []

        url = f"{self.base_url}/{page_id}/posts"
        params = {
            "access_token": self.access_token,
            "fields": "id,message,created_time,permalink_url,reactions.summary(true)",
            "limit": limit
        }

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            logger.error("Error fetching Facebook posts", page_id=page_id, error=str(e))
            return []


class SocialMediaCollector:
    """Unified social media data collector."""

    def __init__(self):
        self.twitter = TwitterAPI()
        self.facebook = None  # Initialize only if needed

    async def collect_official_social_data(self, official: Dict) -> Dict:
        """Collect all social media data for an official."""
        social_data = {
            "twitter": {},
            "facebook": {},
            "instagram": {},  # Placeholder for future implementation
            "collection_date": datetime.now().isoformat()
        }

        # Twitter data
        if official.get("twitter_handle"):
            twitter_handle = official["twitter_handle"].replace("@", "")

            twitter_user = await self.twitter.get_user_by_username(twitter_handle)
            if twitter_user:
                social_data["twitter"]["profile"] = twitter_user

                # Get recent tweets
                tweets = await self.twitter.get_user_tweets(twitter_handle, max_results=200)
                social_data["twitter"]["recent_tweets"] = tweets

                # Search for policy-related tweets
                policy_keywords = [
                    "healthcare", "economy", "education", "environment",
                    "immigration", "defense", "infrastructure", "taxes"
                ]

                policy_tweets = []
                for keyword in policy_keywords:
                    keyword_tweets = await self.twitter.search_tweets_by_user(
                        twitter_handle, keyword, max_results=10
                    )
                    policy_tweets.extend(keyword_tweets)

                social_data["twitter"]["policy_tweets"] = policy_tweets

        # Facebook data (if page URL provided)
        if official.get("facebook_url") and self.facebook:
            # Extract page ID from URL - simplified approach
            try:
                page_id = official["facebook_url"].split("/")[-1]
                page_info = await self.facebook.get_page_info(page_id)
                if page_info:
                    social_data["facebook"]["profile"] = page_info
                    posts = await self.facebook.get_page_posts(page_id, limit=100)
                    social_data["facebook"]["recent_posts"] = posts
            except Exception as e:
                logger.error("Error processing Facebook URL", url=official["facebook_url"], error=str(e))

        return social_data