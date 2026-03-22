import { useEffect, useRef, useState } from "react";
import DatetimeRenderer from "../DatetimeRenderer";
import { MessageResponse } from "../../types/message";
import ReactMarkdown from "react-markdown";
import { CopyOutlined, CheckOutlined } from "@ant-design/icons";
import { Button, Tooltip, Modal } from "antd";
import rehypeRaw from 'rehype-raw';
import { Wand2 } from "lucide-react";

export default function MessageList({
  messages,
}: {
  messages: MessageResponse[];
}) {
  const messageEndRef = useRef<HTMLDivElement>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: "instant" });
  }, [messages]);

  const handleCopy = (content: string, messageId: string) => {
    navigator.clipboard.writeText(content);
    setCopiedMessageId(messageId);
    setTimeout(() => {
      setCopiedMessageId(null);
    }, 3000);
  };

  return (
    <div className="flex-1 overflow-y-auto space-y-4 bg-white rounded-xl shadow-card">
      <div className="p-6 rounded-lg" style={{
        background: 'white'
      }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start mb-6 ${msg.role === "USER" ? "justify-end" : ""}`}
          >
            {msg.role !== "USER" && (
              <div className="bg-purple-100 rounded-full p-2.5 mr-3 flex-shrink-0 shadow-sm">
                <Wand2 className="w-5 h-5 text-purple-600" />
              </div>
            )}
            <div
              className={`rounded-lg p-4 max-w-[70%] shadow-sm ${msg.role === "USER"
                  ? "bg-gray-50 border border-gray-100"
                  : msg.id.startsWith("processing-")
                    ? "bg-gradient-to-r from-[#7c5aff10] to-[#5cb8e610] animate-pulse"
                    : "bg-gradient-to-r from-[#7c5aff10] to-[#5cb8e610]"
                }`}
            >
              <div className={`prose prose-sm max-w-none text-gray-700`}>
                <ReactMarkdown rehypePlugins={[rehypeRaw]}>{msg.content}</ReactMarkdown>
              </div>
              <div className="flex items-center justify-between mt-2">
                <p className="text-xs text-gray-500">
                  <DatetimeRenderer>{msg.created_at}</DatetimeRenderer>
                </p>
                {msg.role !== "USER" && !msg.id.startsWith("processing-") && (
                  <Tooltip
                    title={
                      copiedMessageId === msg.id
                        ? "Đã sao chép!"
                        : "Sao chép tin nhắn"
                    }
                  >
                    <Button
                      type={copiedMessageId === msg.id ? "primary" : "text"}
                      shape="circle"
                      size="small"
                      className={`transition-all duration-300 flex items-center justify-center hover:bg-gradient-to-r hover:from-[#7c5aff20] hover:to-[#5cb8e620] ${copiedMessageId === msg.id
                          ? "bg-gradient-to-r from-[#7c5aff] to-[#5cb8e6] text-white transform scale-105"
                          : ""
                        }`}
                      icon={
                        copiedMessageId === msg.id ? (
                          <CheckOutlined style={{ fontSize: "14px" }} />
                        ) : (
                          <CopyOutlined
                            style={{ fontSize: "14px", opacity: 0.7 }}
                          />
                        )
                      }
                      onClick={() => handleCopy(msg.content, msg.id)}
                    />
                  </Tooltip>
                )}
              </div>
            </div>
            {msg.role === "USER" && (
              <div className="bg-blue-100 rounded-full p-2.5 ml-3 flex-shrink-0 shadow-sm">
                <svg className="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            )}
          </div>
        ))}
        <div ref={messageEndRef} />
      </div>
      <Modal
        open={!!selectedImage}
        footer={null}
        onCancel={() => setSelectedImage(null)}
        width="90vw"
        centered
        className="image-modal"
      >
        {selectedImage && (
          <img
            src={selectedImage}
            alt="preview"
            className="w-full h-auto max-h-[90vh] object-contain"
          />
        )}
      </Modal>
    </div>
  );
}
