import { useState } from "react";
import { sendMessage } from "../services/api";

export default function useChat(accessToken) {

    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const [sessionId, setSessionId] = useState(
        localStorage.getItem("budgetwise_session_id") || null
    );

    const [conversations, setConversations] = useState([]);
    const [activeId, setActiveId] = useState(null);

    async function send(text){

        if(!text.trim()) return;

        if(!accessToken){
            alert("Please login first");
            return;
        }

        let currentSession=sessionId;

        // First message -> create new conversation
        if(!currentSession){

            currentSession=crypto.randomUUID();

            setSessionId(currentSession);

            setActiveId(currentSession);

            localStorage.setItem(
                "budgetwise_session_id",
                currentSession
            );

            setConversations(prev=>[
                {
                    id:currentSession,
                    title:text.substring(0,30)+"...",
                    date:new Date().toLocaleDateString()
                },
                ...prev
            ]);

        }

        setMessages(prev=>[
            ...prev,
            {
                role:"user",
                text
            }
        ]);

        setLoading(true);

        setMessages(prev=>[
            ...prev,
            {
                role:"assistant",
                text:""
            }
        ]);

        try{

            const result=await sendMessage(

                text,
                currentSession,
                accessToken,

                (chunk)=>{

                    setMessages(prev=>{

                        const copy=[...prev];

                        copy[copy.length-1].text+=chunk;

                        return copy;

                    });

                }

            );

            if(result.sessionId){

                setSessionId(result.sessionId);

                setActiveId(result.sessionId);

                localStorage.setItem(
                    "budgetwise_session_id",
                    result.sessionId
                );

            }

        }

        finally{

            setLoading(false);

        }

    }

    function newChat(){

        setMessages([]);

        setSessionId(null);

        setActiveId(null);

        localStorage.removeItem(
            "budgetwise_session_id"
        );

    }

    return{

        messages,
        loading,
        send,
        newChat,

        conversations,
        activeId

    };

}