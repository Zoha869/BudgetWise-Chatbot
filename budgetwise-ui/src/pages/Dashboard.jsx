import { useEffect, useState } from "react";
import "../styles/dashboard.css";

import Sidebar from "../components/Sidebar";
import Chat from "../components/Chat";

import useChat from "../hooks/useChat";
import { supabase } from "../services/supabase";

function Dashboard() {

  const [user, setUser] = useState(null);
  const [token, setToken] = useState("");

  useEffect(() => {

    async function loadUser() {

      const { data } = await supabase.auth.getSession();

      if (data.session) {
        setUser(data.session.user);
        setToken(data.session.access_token);
      }

    }

    loadUser();

  }, []);


const {
    messages,
    loading,
    send,
    newChat,
    conversations,
    activeId,
    selectConversation
} = useChat(token);

  async function logout() {

    await supabase.auth.signOut();

    window.location.reload();

  }


  return (

    <div className="dashboard">
<Sidebar
  user={user}
  conversations={conversations}
  activeId={activeId}
  onNewChat={newChat}
  onSelectConversation={selectConversation}
  onLogout={logout}
/>


      <div className="dashboard-content">

        <Chat

          messages={messages}

          loading={loading}

          onSend={send}

        />

      </div>


    </div>

  );

}

export default Dashboard;