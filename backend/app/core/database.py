import logging

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """
    Returns a configured Supabase client using the service role key.
    This client bypasses RLS and should only be used for server-side operations.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.error("Supabase URL or Service Key is missing in environment variables.")
        raise ValueError("Missing Supabase credentials")

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


# Singleton instance for general use
supabase: Client = get_supabase_client()
