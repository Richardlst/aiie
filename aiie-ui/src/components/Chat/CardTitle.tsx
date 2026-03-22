import { ChevronLeft } from "lucide-react";
import { ConversationResponse } from "../../types/conversation";

export default function CardTitle({
  showConversations,
  currentConversation,
  handBackClick,
}: {
  showConversations: boolean;
  currentConversation?: ConversationResponse;
  handBackClick: () => void;
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center">
        {!showConversations && (
          <div className="p-1.5 rounded-full hover:bg-gradient-to-r hover:from-[#7c5aff20] hover:to-[#5cb8e620] transition-all duration-300">
            <ChevronLeft
              className="w-5 h-5 cursor-pointer text-gray-600 hover:text-[#7c5aff]"
              onClick={handBackClick}
            />
          </div>
        )}
        <span className="font-medium text-gray-800 px-1">
          {showConversations ? (
            "Conversations"
          ) : (
            <span>
              {currentConversation?.name || "New conversation"}
            </span>
          )}
        </span>
      </div>
    </div>
  );
}
