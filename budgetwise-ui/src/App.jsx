import { useEffect, useState } from "react";

import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

import { supabase } from "./services/supabase";
import { ThemeProvider } from "./context/ThemeContext";

function App() {

  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {

    async function getSession() {
      const { data } = await supabase.auth.getSession();
      setSession(data.session);
      setLoading(false);
    }

    getSession();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        setSession(session);
      }
    );

    return () => {
      listener.subscription.unsubscribe();
    };

  }, []);

  if (loading) {
    return (
      <div
        style={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "22px"
        }}
      >
        Loading...
      </div>
    );
  }

  return (
    <ThemeProvider>
      {session ? <Dashboard /> : <Home />}
    </ThemeProvider>
  );
}

export default App;