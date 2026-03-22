export type ConversationResponse = {
    id: string;
    name?: string;
    created_at: string;
    updated_at: string | null;
}

export type WSResponseType = "processing";

export type WSResponseDataProcessing = {
    process_name: string;
}

export type WSResponseData = WSResponseDataProcessing;

export type WSResponse = {
    type: WSResponseType;
    data: WSResponseData;
}
