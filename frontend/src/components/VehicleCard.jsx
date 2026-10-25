import { useState } from "react";

import VehicleForm from "./VehicleForm";
import { Alert, Button, ConfirmDialog, formatPrice } from "./ui";

// One vehicle: details, a purchase control for everyone and admin tools.
// `actions` holds the API calls; each returns a promise so the card can show progress.
export default function VehicleCard({ vehicle, isAdmin, actions }) {
  const [buyQty, setBuyQty] = useState("1");
  const [restockQty, setRestockQty] = useState("1");
  const [editing, setEditing] = useState(false);
  const [confirmQty, setConfirmQty] = useState(null);
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState({ kind: "error", text: "" });

  const name = `${vehicle.make} ${vehicle.model}`;
  const soldOut = vehicle.quantity === 0;

  async function run(actionName, action, successText) {
    setBusy(actionName);
    setMessage({ kind: "error", text: "" });
    try {
      await action();
      if (successText) setMessage({ kind: "success", text: successText });
    } catch (error) {
      const text =
        actionName === "buy" && error.status === 409
          ? "Not enough stock left. The inventory has been refreshed."
          : error.message;
      setMessage({ kind: "error", text });
    } finally {
      setBusy("");
    }
  }

  function positiveWhole(value) {
    const number = Number(value);
    return Number.isInteger(number) && number > 0 ? number : null;
  }

  function handleBuy() {
    const qty = positiveWhole(buyQty);
    if (!qty) return setMessage({ kind: "error", text: "Enter a whole number above 0" });
    if (qty > vehicle.quantity) {
      return setMessage({ kind: "error", text: `Only ${vehicle.quantity} in stock` });
    }
    setMessage({ kind: "error", text: "" });
    setConfirmQty(qty);
  }

  function confirmBuy() {
    const qty = confirmQty;
    setConfirmQty(null);
    run("buy", () => actions.purchase(vehicle.id, qty), `Purchased ${qty} × ${name}`);
  }

  function handleRestock() {
    const qty = positiveWhole(restockQty);
    if (!qty) return setMessage({ kind: "error", text: "Enter a whole number above 0" });
    run("restock", () => actions.restock(vehicle.id, qty), `Restocked ${qty}`);
  }

  function handleDelete() {
    if (!window.confirm(`Delete ${name}?`)) return;
    run("delete", () => actions.remove(vehicle.id));
  }

  if (editing) {
    return (
      <article className="panel">
        <h3 className="panel-title">Edit vehicle</h3>
        <VehicleForm
          initial={vehicle}
          submitLabel="Save"
          onCancel={() => setEditing(false)}
          onSubmit={async (values) => {
            await actions.update(vehicle.id, values);
            setEditing(false);
          }}
        />
      </article>
    );
  }

  return (
    <article className="panel flex flex-col gap-4">
      <header className="flex items-start justify-between gap-3">
        <div>
          <span className="chip">{vehicle.category}</span>
          <h3 className="mt-2 font-display text-2xl leading-tight">
            {vehicle.make} <span className="text-teal-dark">{vehicle.model}</span>
          </h3>
        </div>
        {soldOut && <span className="stamp">Sold out</span>}
      </header>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="plate">{formatPrice(vehicle.price)}</span>
        <span className="flex items-center gap-2 text-xs font-bold tracking-widest uppercase">
          In stock
          <span className={`gauge ${soldOut ? "gauge-empty" : ""}`}>
            {String(vehicle.quantity).padStart(3, "0")}
          </span>
        </span>
      </div>

      <div className="flex items-end gap-2">
        <label className="flex w-20 flex-col gap-1">
          <span className="field-label">Qty</span>
          <input
            className="field"
            type="number"
            min="1"
            max={vehicle.quantity}
            value={buyQty}
            onChange={(event) => setBuyQty(event.target.value)}
            disabled={soldOut}
          />
        </label>
        <Button
          variant="red"
          className="flex-1"
          onClick={handleBuy}
          busy={busy === "buy"}
          disabled={soldOut || Boolean(busy)}
        >
          {soldOut ? "Sold out" : "Buy"}
        </Button>
      </div>

      {isAdmin && (
        <div className="flex flex-col gap-3 border-t-2 border-dashed border-steel/40 pt-4">
          <span className="field-label">Admin</span>
          <div className="flex items-end gap-2">
            <label className="flex w-20 flex-col gap-1">
              <span className="field-label">Qty</span>
              <input
                className="field"
                type="number"
                min="1"
                value={restockQty}
                onChange={(event) => setRestockQty(event.target.value)}
              />
            </label>
            <Button
              variant="teal"
              className="flex-1"
              onClick={handleRestock}
              busy={busy === "restock"}
              disabled={Boolean(busy)}
            >
              Restock
            </Button>
          </div>
          <div className="flex gap-2">
            <Button className="flex-1" onClick={() => setEditing(true)} disabled={Boolean(busy)}>
              Edit
            </Button>
            <Button
              className="flex-1"
              onClick={handleDelete}
              busy={busy === "delete"}
              disabled={Boolean(busy)}
            >
              Delete
            </Button>
          </div>
        </div>
      )}

      <Alert kind={message.kind}>{message.text}</Alert>

      {confirmQty !== null && (
        <ConfirmDialog
          title="Confirm purchase"
          confirmLabel="Confirm purchase"
          onConfirm={confirmBuy}
          onCancel={() => setConfirmQty(null)}
        >
          <p className="font-display text-lg">
            {confirmQty} × {name}
          </p>
          <dl className="mt-3 grid grid-cols-2 gap-y-1 text-sm">
            <dt>Price each</dt>
            <dd className="text-right font-mono">{formatPrice(vehicle.price)}</dd>
            <dt className="font-bold">Total</dt>
            <dd className="text-right font-mono font-bold">
              {formatPrice(vehicle.price * confirmQty)}
            </dd>
          </dl>
        </ConfirmDialog>
      )}
    </article>
  );
}
