import { useState } from "react";

import { useAuth } from "../context/AuthContext";
import { Alert, Button, Field, Panel } from "./ui";

function validate(mode, { email, password, confirm }) {
  const errors = {};
  if (!/^\S+@\S+\.\S+$/.test(email)) errors.email = "Enter a valid email address";
  if (mode === "register") {
    if (password.length < 8) errors.password = "At least 8 characters";
    if (confirm !== password) errors.confirm = "Passwords don't match";
  } else if (!password) {
    errors.password = "Enter your password";
  }
  return errors;
}

export default function AuthPage() {
  const { login, register, notice } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [busy, setBusy] = useState(false);

  const isRegister = mode === "register";
  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  function switchMode() {
    setMode(isRegister ? "login" : "register");
    setErrors({});
    setServerError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const found = validate(mode, form);
    setErrors(found);
    setServerError("");
    if (Object.keys(found).length) return;

    setBusy(true);
    try {
      if (isRegister) await register(form.email, form.password);
      else await login(form.email, form.password);
    } catch (error) {
      setServerError(error.message);
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-6 px-4 py-10">
      <div className="chrome flex flex-col items-center gap-3 rounded-2xl px-6 py-5">
        <span className="emblem chrome">AutoDeal</span>
        <div className="grille w-full" />
        <p className="text-sm font-semibold tracking-widest text-ink/70 uppercase">
          Dealership inventory
        </p>
      </div>

      <Panel title={isRegister ? "Create an account" : "Sign in"}>
        <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
          <Alert kind="error">{notice}</Alert>
          <Field
            label="Email"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={update("email")}
            error={errors.email}
          />
          <Field
            label="Password"
            type="password"
            autoComplete={isRegister ? "new-password" : "current-password"}
            value={form.password}
            onChange={update("password")}
            error={errors.password}
          />
          {isRegister && (
            <Field
              label="Confirm password"
              type="password"
              autoComplete="new-password"
              value={form.confirm}
              onChange={update("confirm")}
              error={errors.confirm}
            />
          )}
          <Alert kind="error">{serverError}</Alert>
          <Button type="submit" variant="red" busy={busy}>
            {isRegister ? "Register" : "Start engine"}
          </Button>
        </form>

        <p className="mt-5 text-center text-sm">
          {isRegister ? "Already have an account?" : "New here?"}{" "}
          <button type="button" onClick={switchMode} className="font-bold text-teal-dark underline">
            {isRegister ? "Sign in" : "Create an account"}
          </button>
        </p>
      </Panel>
    </main>
  );
}
