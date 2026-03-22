import { useEffect, useRef, useState } from "react";
import { Card, message, Upload, Button, Modal } from "antd";
import { Send, Image as ImageIcon, X } from "lucide-react";
import type { UploadFile, UploadProps } from "antd/es/upload/interface";
import {
  ConversationResponse,
  WSResponse,
  WSResponseDataProcessing,
} from "../../types/conversation";
import {
  createConversationApi,
  getConversationsApi,
} from "../../services/apis/conversation";
import {
  AddMessageRequest,
  AddMessageResponse,
  MessageResponse,
} from "../../types/message";
import {
  addMessageApi,
  getMessagesByConversationIdApi,
} from "../../services/apis/message";
import Loading from "../Loading";
import { useAuth } from "../../contexts/AuthContext";
import CardTitle from "./CardTitle";
import CardExtra from "./CardExtra";
import ConversationList from "./ConversationList";
import MessageList from "./MessageList";
import { saveMultipleImage } from "../../services/apis";
import { getBase64 } from "../../utils";
import processMap, { type ProcessName } from "./processMap";

const VITE_AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL;

interface ChatProps {
  onClose: () => void;
}

export default function Chat({ onClose }: ChatProps) {
  const { authData } = useAuth();
  const accessToken = authData?.accessToken;

  const [isLoading, setIsLoading] = useState(true);
  const [disableChat, setDisableChat] = useState(false);

  const [conversations, setConversations] = useState<ConversationResponse[]>(
    []
  );
  const [showConversations, setShowConversations] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState<
    string | null
  >(null);
  const currentConversation = conversations.find(
    (conv) => conv.id === selectedConversation
  );

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState("");
  const [previewTitle, setPreviewTitle] = useState("");

  const socket = useRef<WebSocket | null>(null);

  const [messageApi, messageContextHolder] = message.useMessage();

  // Fetch conversations
  useEffect(() => {
    const fetchConversations = async () => {
      const response = await getConversationsApi();

      if (response.status === 200) {
        const responseData: ConversationResponse[] = response.data;
        setConversations(responseData);
      }
      setIsLoading(false);
    };

    fetchConversations();
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (!accessToken || !selectedConversation) return;

    const connectWebSocket = () => {
      socket.current = new WebSocket(
        `${VITE_AGENT_API_URL}/conversation/ws/${selectedConversation}?access_token=${accessToken}`
      );

      let pingInterval: number | undefined;

      socket.current.onopen = () => {
        console.log("WebSocket connected");

        // Thiết lập ping định kỳ
        pingInterval = setInterval(() => {
          if (socket.current && socket.current.readyState === WebSocket.OPEN) {
            socket.current.send("pong");
          }
        }, 15000); // 15 giây
      };

      socket.current.onmessage = (event) => {
        if (event.data === "ping") {
          // Nhận được ping từ server, trả lại pong
          if (socket.current && socket.current.readyState === WebSocket.OPEN) {
            socket.current.send("pong");
          }
          return;
        }

        try {
          const response = JSON.parse(event.data) as WSResponse;
          switch (response.type) {
            case "processing": {
              // Xử lý response
              const responseData = response.data as WSResponseDataProcessing;
              const processingMessage: MessageResponse = {
                id: `processing-${Date.now()}`,
                content: processMap[responseData.process_name as ProcessName],
                role: "ASSISTANT",
                conversation_id: selectedConversation,
                created_at: new Date().toISOString(),
                updated_at: null,
              };
              removeProcessingMessage();
              addMessage([processingMessage]);
              break;
            }
            default:
              break;
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      socket.current.onclose = (event) => {
        console.log(
          `WebSocket closed with code ${event.code}: ${event.reason}`
        );

        if (pingInterval) {
          clearInterval(pingInterval);
        }

        // Thử kết nối lại sau 5 giây nếu đóng không phải do người dùng chủ động
        if (event.code !== 1000) {
          setTimeout(connectWebSocket, 5000);
        }
      };

      socket.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    };

    connectWebSocket();

    return () => {
      if (socket.current) {
        // Đóng kết nối với mã 1000 (đóng bình thường)
        socket.current.close(1000, "User navigated away");
      }

      // Cleanup timeouts and intervals
      const ws = socket.current;
      if (ws) {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onclose = null;
        ws.onerror = null;
      }
    };
  }, [accessToken, selectedConversation]);

  // Conversation details
  const handleConversationClick = async (conversationId: string) => {
    setSelectedConversation(conversationId);
    setShowConversations(false);
    setIsLoading(true);
    const response = await getMessagesByConversationIdApi(conversationId);
    setIsLoading(false);
    const responseData: MessageResponse[] = response.data;
    setMessages(responseData);
  };

  // Back to conversations list
  const handBackClick = () => {
    setShowConversations(true);
    setSelectedConversation(null);
    setMessages([]);
    setFileList([]);
    setInput("");
  };

  // Create new conversation
  const handleCreateNewConversation = async () => {
    setIsLoading(true);
    const response = await createConversationApi();
    setIsLoading(false);
    if (response.status === 200) {
      const responseData: ConversationResponse = response.data;
      const newConversation: ConversationResponse = {
        id: responseData.id,
        name: responseData.name,
        created_at: responseData.created_at,
        updated_at: responseData.updated_at,
      };
      setConversations((prev) => [newConversation, ...prev]);
      setSelectedConversation(newConversation.id);
      setShowConversations(false);
    } else {
      console.error("Error creating new conversation:", response.data);
    }
  };

  // Send message
  const handleSendMessage = async () => {
    if ((!input.trim() && fileList.length === 0) || !selectedConversation)
      return;
    if (!socket.current) return;

    removeTempMessage();

    // Display temp message with image placeholders
    setDisableChat(true);
    setInput("");
    setFileList([]);

    const currentInput = input;
    const currentFileList = fileList;

    try {
      let stubMessage: MessageResponse = {
        id: `temp-${Date.now()}`,
        content: currentInput,
        role: "USER",
        conversation_id: selectedConversation,
        created_at: new Date().toISOString(),
        updated_at: null,
      };
      addMessage([stubMessage]);

      // Upload images if any
      let uploadedFiles: string[] = [];
      if (fileList.length > 0) {
        const responseData = await saveMultipleImage(fileList);
        uploadedFiles = responseData.data.map((file) => file.url);
      }
      const imageString =
        "\n" + uploadedFiles.map((file) => `![${file}](${file})`).join("\n");
      const newContent = currentInput + imageString;

      removeTempMessage();
      stubMessage.content = newContent;
      addMessage([stubMessage]);

      const request: AddMessageRequest = {
        conversation_id: selectedConversation,
        content: newContent,
        files: uploadedFiles,
      };

      const response = await addMessageApi(request);

      const responseData: AddMessageResponse = response.data;
      addMessage(responseData.messages);

      // Update conversation name
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === selectedConversation
            ? { ...conv, name: responseData.conversation.name }
            : conv
        )
      );
    } catch (error) {
      console.error(error);
      messageApi.error("Error sending message");
      setInput(currentInput);
      setFileList(currentFileList);
    } finally {
      removeTempMessage();
      removeProcessingMessage();
      setDisableChat(false);
    }
  };

  // Remove temp message
  const removeTempMessage = () => {
    setMessages((prev) => prev.filter((msg) => !msg.id.startsWith("temp-")));
  };

  // Remove processing message
  const removeProcessingMessage = () => {
    setMessages((prev) =>
      prev.filter((msg) => !msg.id.startsWith("processing-"))
    );
  };

  // Add message
  const addMessage = (messages: MessageResponse[]) => {
    setMessages((prev) => [...prev, ...messages]);
  };

  // Image upload handlers
  const handlePreview = async (file: UploadFile) => {
    if (!file.url && !file.preview) {
      file.preview = await getBase64(file.originFileObj as Blob);
    }
    setPreviewImage(file.url || (file.preview as string));
    setPreviewOpen(true);
    setPreviewTitle(
      file.name || file.url!.substring(file.url!.lastIndexOf("/") + 1)
    );
  };

  const handleCancel = () => setPreviewOpen(false);

  const handleChange: UploadProps["onChange"] = async ({
    fileList: newFileList,
  }) => {
    // Cập nhật preview cho tất cả các file mới
    const updatedFileList = await Promise.all(
      newFileList.map(async (file) => {
        if (!file.url && !file.preview) {
          file.preview = await getBase64(file.originFileObj as Blob);
        }
        return file;
      })
    );
    setFileList(updatedFileList);
  };

  return (
    <Card
      className="w-[450px] h-[600px] shadow-lg z-50 bg-gray-50 max-w-[92vw]"
      title={
        <CardTitle
          showConversations={showConversations}
          currentConversation={currentConversation}
          handBackClick={handBackClick}
        />
      }
      extra={
        <CardExtra
          showConversations={showConversations}
          handleCreateNewConversation={handleCreateNewConversation}
          onClose={onClose}
        />
      }
      styles={{
        body: { padding: 0, height: "calc(100% - 57px)" },
      }}
    >
      {messageContextHolder}
      <div className="flex flex-col h-full bg-white">
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <Loading
              message={
                showConversations
                  ? "Loading conversations..."
                  : "Loading messages..."
              }
            />
          </div>
        ) : showConversations ? (
          // List of conversations tab
          <ConversationList
            conversations={conversations}
            handleConversationClick={handleConversationClick}
          />
        ) : (
          // List of messages tab
          <>
            <MessageList messages={messages} />

            <div className="border-t p-2 bg-white">
              {fileList.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2 p-2 bg-gray-50 rounded-md">
                  {fileList.map((file, index) => (
                    <div key={file.uid} className="relative">
                      <div
                        className="w-16 h-16 rounded bg-gray-200 overflow-hidden cursor-pointer"
                        onClick={() => handlePreview(file)}
                      >
                        <img
                          src={file.thumbUrl || (file.preview as string)}
                          alt={file.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <Button
                        type="text"
                        size="small"
                        className="absolute -top-2 -right-2 p-0 w-5 h-5 flex items-center justify-center bg-gray-100 rounded-full border shadow-sm"
                        onClick={() => {
                          const newFileList = [...fileList];
                          newFileList.splice(index, 1);
                          setFileList(newFileList);
                        }}
                        icon={<X className="w-3 h-3" />}
                      />
                    </div>
                  ))}
                </div>
              )}

              <div className="flex items-center space-x-2">
                <Upload
                  fileList={[]}
                  onPreview={handlePreview}
                  onChange={handleChange}
                  className="upload-list-inline"
                  showUploadList={false}
                  beforeUpload={(file) => {
                    const isImage = file.type.startsWith("image/");
                    if (!isImage) {
                      messageApi.error("You can only upload image files!");
                      return false;
                    }

                    // Generate preview for immediate display
                    const reader = new FileReader();
                    reader.onload = () => {
                      const newFile: UploadFile = {
                        uid: Date.now().toString(),
                        name: file.name,
                        status: "done",
                        url: "",
                        originFileObj: file,
                        thumbUrl: reader.result as string,
                      };
                      setFileList([...fileList, newFile]);
                    };
                    reader.readAsDataURL(file);

                    // Return false to prevent auto upload

                    const isLt10M = file.size / 1024 / 1024 < 10;
                    if (!isLt10M) {
                      messageApi.error("File size must be smaller than 10MB!");
                      return Upload.LIST_IGNORE;
                    }
                    
                    return false;
                  }}
                  disabled={disableChat}
                  multiple
                >
                  <Button
                    size="middle"
                    shape="circle"
                    icon={
                      <ImageIcon
                        className="w-4 h-4"
                        style={{ display: "block", margin: "0 auto" }}
                      />
                    }
                    type={fileList.length > 0 ? "primary" : "default"}
                    disabled={disableChat}
                  />
                </Upload>

                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyUp={(e) =>
                    e.key === "Enter" && !e.shiftKey && handleSendMessage()
                  }
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 border rounded-full focus:outline-none focus:border-blue-500 bg-gray-50"
                  disabled={disableChat}
                />

                <Button
                  disabled={
                    disableChat || (!input.trim() && fileList.length === 0)
                  }
                  icon={
                    <Send
                      className="w-4 h-4"
                      style={{ display: "block", margin: "0 auto" }}
                    />
                  }
                  onClick={handleSendMessage}
                  className="p-4 rounded-full bg-blue-500 text-white transition-colors flex items-center justify-center "
                />
              </div>
            </div>
          </>
        )}
      </div>

      <Modal
        open={previewOpen}
        title={previewTitle}
        footer={null}
        onCancel={handleCancel}
      >
        <img alt="preview" style={{ width: "100%" }} src={previewImage} />
      </Modal>
    </Card>
  );
}
