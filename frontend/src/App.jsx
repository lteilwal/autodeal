import AuthPage from "./components/AuthPage";
import Dashboard from "./components/Dashboard";
import { Spinner } from "./components/ui";
import { useAuth } from "./context/AuthContext";

// Shows the login/register screen or the dashboard, depending on who is logged in.
export default function App() {
  const { user, checking } = useAuth();

  if (checking) return <Spinner label="Checking your session…" />;
  return user ? <Dashboard /> : <AuthPage />;
}
