import { ChevronRight, MessageSquare } from "lucide-react";
import DatetimeRenderer from "../DatetimeRenderer";
import { ConversationResponse } from "../../types/conversation";

export default function ConversationList({
  conversations,
  handleConversationClick,
}: {
  conversations: ConversationResponse[];
  handleConversationClick: (id: string) => void;
}) {
  return (
    <div className="flex-1 overflow-y-auto space-y-2 p-4 bg-white">
      {conversations.map((conv) => (
        <div
          key={conv.id}
          className="rounded-lg border border-gray-100 hover:border-transparent hover:shadow-md cursor-pointer transition-all duration-300 group"
          onClick={() => {
            handleConversationClick(conv.id);
          }}
        >
          <div className="p-4 hover:bg-gradient-to-r hover:from-[#7c5aff10] hover:to-[#5cb8e610] rounded-lg">
            <div className="flex items-start space-x-3">
              <div className="p-2 rounded-lg bg-purple-50 group-hover:bg-purple-100 transition-colors">
                <MessageSquare className="w-5 h-5 text-purple-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-sm text-gray-800 group-hover:text-purple-600 transition-colors">
                  {conv.name || "New conversation"}
                </h3>
                <p className="text-gray-500 text-xs mt-1">
                  <DatetimeRenderer>{conv.created_at}</DatetimeRenderer>
                </p>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-purple-400 transition-colors" />
            </div>
          </div>
        </div>
      ))}
      {conversations.length === 0 && (
        <div className="text-center py-8">
          <div className="bg-gray-50 inline-block p-3 rounded-full mb-3">
            <MessageSquare className="w-6 h-6 text-gray-400" />
          </div>
          <p className="text-gray-500 text-sm">No conversations yet</p>
        </div>
      )}
    </div>
  );
}
