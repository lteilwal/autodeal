// Small building blocks shared by every screen. The look lives in index.css.

import { useEffect, useId } from "react";

export function Button({
  variant = "chrome",
  busy = false,
  disabled = false,
  children,
  className = "",
  ...props
}) {
  return (
    <button className={`btn btn-${variant} ${className}`} disabled={busy || disabled} {...props}>
      {busy ? "Working…" : children}
    </button>
  );
}

export function Panel({ title, children, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      {title && <h2 className="panel-title">{title}</h2>}
      {children}
    </section>
  );
}

export function Field({ label, error, className = "", ...inputProps }) {
  return (
    <label className={`flex flex-col gap-1 ${className}`}>
      <span className="field-label">{label}</span>
      <input className={`field ${error ? "field-invalid" : ""}`} {...inputProps} />
      {error && <span className="text-xs font-semibold text-cherry-dark">{error}</span>}
    </label>
  );
}

export function Alert({ kind = "error", children }) {
  if (!children) return null;
  return (
    <p role={kind === "error" ? "alert" : "status"} className={`alert alert-${kind}`}>
      {children}
    </p>
  );
}

export function Spinner({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-10 text-cream" role="status">
      <span className="hubcap" aria-hidden="true" />
      <span className="font-display tracking-wider">{label}</span>
    </div>
  );
}

// Modal yes/no prompt. Escape or clicking the backdrop cancels.
export function ConfirmDialog({ title, confirmLabel, onConfirm, onCancel, children }) {
  const titleId = useId();

  useEffect(() => {
    const handleKey = (event) => event.key === "Escape" && onCancel();
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onCancel]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/60 p-4"
      onClick={onCancel}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="panel w-full max-w-sm"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id={titleId} className="panel-title">
          {title}
        </h2>
        {children}
        <div className="mt-5 flex justify-end gap-3">
          <Button onClick={onCancel} autoFocus>
            Cancel
          </Button>
          <Button variant="red" onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

const priceFormat =new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
export const formatPrice = (price) => priceFormat.format(price);
