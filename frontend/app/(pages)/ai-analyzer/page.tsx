"use client";
import Hero from "@/components/ai-analyzer/Hero";
import { useState } from "react";
import { Loader2, MessageSquare, Send } from "lucide-react";
import { authFetchClient } from "@/lib/api/authFetchClient";
import Conversation from "@/types/conversation";
import { useRouter } from "next/navigation";

interface Suggestion {
  id: string;
  label: string;
}

const SUGGESTIONS: Suggestion[] = [
  { id: "1", label: "What is the most sold product in Saudi Arabia?" },
  { id: "2", label: "Create a growth projection chart" },
  {
    id: "3",
    label: "Which products are running low on stock (below 20 units)?",
  },
  {
    id: "4",
    label: "Can the same product have different unit prices across purchases?",
  },
  { id: "5", label: "Predict next week's inventory needs" },
];

const ChatPart = () => {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input;
    setInput("");
    setError(null);
    try {
      setIsLoading(true);
      const res = await authFetchClient(`/api/conversations/`, {
        method: "POST",
        body: JSON.stringify({ prompt: userMsg }),
      });

      if (!res.ok) {
        throw new Error("Failed to fetch conversation");
      }
      const conv: Conversation = await res.json();

      console.log(conv);

      if (conv.id) {
        router.push(`/ai-analyzer/${conv.id}`);
      } else {
        throw new Error("No conversation ID received");
      }
    } catch (error) {
      console.error(error);
      setError("Sorry. An error occurred while generating the response.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-full">
      <Hero hide={isLoading} />
      <div className="w-full max-w-4xl mx-auto p-6 space-y-4">
        {!isLoading && (
          <div className="flex items-center gap-2 overflow-x-auto pb-2 no-scrollbar">
            {SUGGESTIONS.map((sug) => (
              <button
                key={sug.id}
                onClick={() => setInput(sug.label)}
                className="whitespace-nowrap px-4 py-2 rounded-full border border-gray-200 text-sm text-text-secondary hover:border-text-active hover:text-text-active transition-all bg-white shadow-sm shrink-0">
                {sug.label}
              </button>
            ))}
          </div>
        )}

        <div className="relative group">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            {isLoading ? (
              <Loader2 className="animate-spin text-text-active" size={20} />
            ) : (
              <div className="relative group/icon pointer-events-auto cursor-help">
                <MessageSquare className="text-text-secondary" size={20} />
                <span
                  role="tooltip"
                  className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-56 px-3 py-2 rounded-lg bg-gray-900 text-white text-xs leading-snug opacity-0 invisible group-hover/icon:opacity-100 group-hover/icon:visible transition-opacity duration-200 shadow-lg z-10">
                  Dots3-Note Preview model will be shut down on Dec 31, 2026.
                </span>
              </div>
            )}
          </div>
          <form onSubmit={handleSend}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                isLoading ? "Thinking..." : "Ask anything about your data..."
              }
              disabled={isLoading}
              className="w-full pl-12 pr-14 py-4 bg-white border border-gray-200 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-text-active/20 focus:border-text-active transition-all text-text-primary disabled:opacity-75"
            />
            {!isLoading && (
              <button
                type="submit"
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-text-active text-white rounded-xl hover:bg-text-active/80 transition-colors disabled:opacity-50"
                disabled={!input.trim()}>
                <Send size={20} />
              </button>
            )}
          </form>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPart;
