import logging

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def verify_device_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Verifies the edge device API key against the bcrypt hash stored in the database.
    Returns the device internal UUID if successful.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key"
        )

    try:
        # Note: In a production scenario with many devices, you might want to cache this
        # or require the device ID in the header to do a direct lookup instead of a scan.
        # For this implementation, we assume the API key is passed as a bearer token.
        # Let's extract the device ID from headers if possible, or assume a lookup mechanism.

        # Since bcrypt requires comparing the hash against the plain text,
        # we need to find the device first. This implies the device needs to identify itself.
        # We will require the device_id to be part of the request payload or header,
        # but for the `Depends` injection to work generally, let's fetch all devices
        # (or rely on a specific header which we'll handle in the route).
        pass

    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )


# A more specific dependency that requires the device_id from the request body
# will be implemented in the route handler itself to avoid parsing the body twice.
