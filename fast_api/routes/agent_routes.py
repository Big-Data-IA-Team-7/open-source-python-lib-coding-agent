import asyncio
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse

from fast_api.services.auth_service import get_current_user
from fast_api.schema.request_schema import HowToRequest, ErrorRequest

from langgraph_graphs.langgraph_agents.error_handling_graph.graph import graph

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-code")
async def generate_code(
    request: HowToRequest,
    current_user: dict = Depends(get_current_user)
) -> StreamingResponse:
    """
    Stream code generation responses based on user query and chat history.
    """
    try:
        if not request.query or request.query.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        async def generate():
            try:
                messages = request.history + [{"role": "user", "content": request.query}]
                
                async for chunk in graph.astream({"messages": messages}):
                    # Ensure we're sending text/event-stream format correctly
                    yield f"data: {str(chunk)}\n\n"
                    
            except asyncio.CancelledError:
                logger.error(f"Stream cancelled by user: {current_user.get('USERNAME')}")
                logger.error(asyncio.CancelledError)
                raise
            except Exception as e:
                logger.error(f"Stream generation error for user {current_user.get('USERNAME')}: {str(e)}")
                yield f"data: Error during code generation: {str(e)}\n\n"
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error during code generation"
                )

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_code for user {current_user.get('USERNAME')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/handle-error")
async def handle_error(
    request: ErrorRequest,
    current_user: dict = Depends(get_current_user)
) -> StreamingResponse:
    """
    Stream code generation responses based on user query and chat history.
    """
    try:
        if not request.task or request.task.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task cannot be empty"
            )

        async def generate():
            try:
                messages = request.history + [{"role": "user", "content": request.task + request.code + request.error}]
                async for chunk in graph.astream({
                    "task": request.task,
                    "code": request.code,
                    "error": request.error,
                    "messages": messages}):
                    # Ensure we're sending text/event-stream format correctly
                    yield f"data: {str(chunk)}\n\n"
                    
            except asyncio.CancelledError:
                logger.error(f"Stream cancelled by user: {current_user.get('USERNAME')}")
                logger.error(asyncio.CancelledError)
                raise
            except Exception as e:
                logger.error(f"Stream generation error for user {current_user.get('USERNAME')}: {str(e)}")
                yield f"data: Error during code generation: {str(e)}\n\n"
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error during code generation"
                )

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in handle_error for user {current_user.get('USERNAME')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )