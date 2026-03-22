import { Plus, X } from "lucide-react";

export default function CardExtra({
  showConversations,
  handleCreateNewConversation,
  onClose,
}: {
  showConversations: boolean;
  handleCreateNewConversation: () => void;
  onClose: () => void;
}) {
  return (
    <span className="flex items-center gap-2">
      {showConversations && (
        <div className="p-1.5 rounded-full hover:bg-gradient-to-r hover:from-[#7c5aff20] hover:to-[#5cb8e620] transition-all duration-300">
          <Plus
            className="w-5 h-5 cursor-pointer text-gray-600 hover:text-[#7c5aff]"
            onClick={handleCreateNewConversation}
          />
        </div>
      )}

      <div className="p-1.5 rounded-full hover:bg-gradient-to-r hover:from-[#7c5aff20] hover:to-[#5cb8e620] transition-all duration-300">
        <X
          className="w-5 h-5 cursor-pointer text-gray-600 hover:text-[#7c5aff]"
          onClick={onClose}
        />
      </div>
    </span>
  );
}
