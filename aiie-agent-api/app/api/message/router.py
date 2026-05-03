import uuid
from typing import List

from fastapi import APIRouter

from app.api.auth.dependencies import AuthenticateDep
from app.api.message.dependencies import MessageServiceDep
from app.api.message.schemas import (
    AddMessageRequest,
    AddMessageResponse,
    MessageResponse,
)

router = APIRouter(prefix="/message", tags=["message"])


@router.get("/{conversation_id}", response_model=List[MessageResponse])
async def get_messages(
    service: MessageServiceDep,
    conversation_id: uuid.UUID,
    token_data: AuthenticateDep,
):
    return await service.get_by_conversation_id(conversation_id, token_data)

@router.post("", response_model=AddMessageResponse)
async def add_message(
    service: MessageServiceDep,
    token_data: AuthenticateDep,
    request: AddMessageRequest,
):
    # Kiểm tra xem Frontend có gửi list 'files' lên không và có phần tử nào không
    if request.files and len(request.files) > 0:
        # Lấy URL của bức ảnh đầu tiên (hoặc bạn có thể nối tất cả nếu muốn)
        first_image_url = request.files[0]
        
        # Nối link ảnh vào đuôi câu lệnh
        request.content = f"{request.content}\n\n[System Note: Hãy sử dụng URL ảnh này để thực thi công cụ: {first_image_url}]"

    # Truyền xuống cho Service xử lý
    return await service.add_message(token_data, request)