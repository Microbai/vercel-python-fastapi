#!/usr/bin/env python
import typing
import pydantic
from fastapi import Header, APIRouter
from openai import AsyncClient
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


class ChatArgs(pydantic.BaseModel):
    model: str
    messages: typing.List[typing.Dict[str, str]]


async def stream_completion(client: AsyncClient, model: str, messages: typing.List[typing.Dict[str, str]]):
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    async for chunk in response:
        yield chunk["choices"][0]["delta"].get("content", "")


@router.post("/chat/completions")
async def groq_api(args: ChatArgs, authorization: str = Header(...)):
    api_key = authorization.split(" ")[1]
    client = AsyncClient(base_url="https://api.groq.com/openai/v1", api_key=api_key)

    # 使用 EventSourceResponse 来处理流式数据
    return EventSourceResponse(stream_completion(client, args.model, args.messages))
