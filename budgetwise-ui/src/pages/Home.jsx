import { useState } from "react";
import Landing from "../components/Landing";
import LoginModal from "../components/LoginModal";
import { supabase } from "../services/supabase";

function Home() {

  const [showLogin, setShowLogin] = useState(false);

  async function handleGoogleLogin() {

    await supabase.auth.signInWithOAuth({

      provider: "google",

      options: {

        redirectTo: window.location.origin

      }

    });

  }

  async function handleEmailLogin(email, password) {

    const { error } = await supabase.auth.signInWithPassword({

      email,

      password

    });

    if (error) {

      alert(error.message);

    }

  }

  return (

    <>

      <Landing
        onLogin={() => setShowLogin(true)}
      />

      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        onGoogleLogin={handleGoogleLogin}
        onEmailLogin={handleEmailLogin}
      />

    </>

  );

}

export default Home;