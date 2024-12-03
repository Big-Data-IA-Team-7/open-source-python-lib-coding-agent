import asyncio
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from fast_api.services.auth_service import get_current_user
from fast_api.schema.request_schema import ChatRequest
from langgraph_graphs.langgraph_agents.code_retrieval_graph.graph import graph

router = APIRouter()

@router.post("/generate-code")
async def generate_code(
    request: ChatRequest,
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
                print(f"Stream cancelled by user: {current_user.get('USERNAME')}")
                print(asyncio.CancelledError)
                raise
            except Exception as e:
                print(f"Stream generation error for user {current_user.get('USERNAME')}: {str(e)}")
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
        print(f"Unexpected error in stream_chat for user {current_user.get('USERNAME')}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )