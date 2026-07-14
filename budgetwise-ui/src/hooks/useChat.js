import { useEffect, useState } from "react";
import { supabase } from "../services/supabase";
import {
    sendMessage,
    getConversations,
    getMessages
} from "../services/api";

export default function useChat(accessToken) {

    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const [sessionId, setSessionId] = useState(
        localStorage.getItem("budgetwise_session_id") || null
    );

    const [conversations, setConversations] = useState([]);
    const [activeId, setActiveId] = useState(null);

    useEffect(() => {

        if (!accessToken) return;

        loadConversations();

    }, [accessToken]);

    async function loadConversations() {

        const data = await getConversations(accessToken);

        setConversations(

            data.map(chat => ({
                id: chat.id,
                title: chat.title || "New Chat",
                date: new Date(chat.created_at).toLocaleDateString()
            }))

        );

    }

    async function send(text) {

        if (!text.trim()) return;

        if (!accessToken) {
            alert("Please login first");
            return;
        }

        let currentSession = sessionId;

        // First message -> create new conversation
        if (!currentSession) {

            currentSession = crypto.randomUUID();

            setSessionId(currentSession);

            setActiveId(currentSession);

            localStorage.setItem(
                "budgetwise_session_id",
                currentSession
            );

        }

        setMessages(prev => [
            ...prev,
            {
                role: "user",
                text,
            },
            {
                role: "assistant",
                text: "",
            },
        ]);

        setLoading(true);

        try {

            const result = await sendMessage(

                text,
                currentSession,
                accessToken,

                (chunk) => {

                    setMessages(prev => {
                        return prev.map((msg, index) => {
                            if (index === prev.length - 1) {
                                return {
                                    ...msg,
                                    text: msg.text + chunk,
                                };
                            }
                            return msg;
                        });
                    });

                }

            );

            const effectiveSessionId = result.sessionId || currentSession;

            setSessionId(effectiveSessionId);

            setActiveId(effectiveSessionId);

            localStorage.setItem(
                "budgetwise_session_id",
                effectiveSessionId
            );

            // Always refresh the sidebar — the backend may generate/update
            // the title even on an existing session, not just brand-new ones.
            await loadConversations();

        }

        finally {

            setLoading(false);

        }

    }

    async function selectConversation(id) {

        const data = await getMessages(
            id,
            accessToken
        );

        setMessages(

            data.map(msg => ({
                role: msg.role,
                text: msg.content
            }))

        );

        setSessionId(id);

        setActiveId(id);

        localStorage.setItem(
            "budgetwise_session_id",
            id
        );

    }

    function newChat() {

        setMessages([]);

        setSessionId(null);

        setActiveId(null);

        localStorage.removeItem(
            "budgetwise_session_id"
        );

    }

    return {
        messages,
        loading,
        send,
        newChat,
        selectConversation,
        conversations,
        activeId
    };
}