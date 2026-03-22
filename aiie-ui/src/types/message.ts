import { ConversationResponse } from "./conversation";

export type WSRequestType = "send" | "cancel";

export interface AddMessageRequest {
    content: string;
    conversation_id: string;
    files?: string[];
}

export interface MessageResponse {
    id: string;
    content: string;
    role: "USER" | "ASSISTANT";
    conversation_id: string;
    created_at: string;
    updated_at: string | null;
}

export interface AddMessageResponse {
    messages: MessageResponse[];
    conversation: ConversationResponse;
}