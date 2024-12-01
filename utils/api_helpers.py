import httpx
import os
from typing import Optional

FAST_API_URL = os.getenv("FAST_API_URL")

async def generatecode_api(user_input: str, history: list, jwt_token: str) -> Optional[httpx.Response]:
    """
    Make async API call to the code generation endpoint.
    
    Args:
        user_input (str): The user's query
        history (list): Chat history
        jwt_token (str): JWT authentication token
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FAST_API_URL}/chat/generate-code",
                json={"query": user_input, "history": history},
                headers={
                    "Accept": "text/event-stream",
                    "Authorization": f"Bearer {jwt_token}"
                },
                timeout=30
            )
            return response
    except Exception as e:
        raise Exception(f"API call failed: {str(e)}")