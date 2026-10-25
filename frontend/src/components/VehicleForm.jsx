import { useState } from "react";

import { Alert, Button, Field } from "./ui";

const BLANK = { make: "", model: "", category: "", price: "", quantity: "" };

// Mirrors the backend rules so most mistakes are caught before a request is sent.
function validate(values) {
  const errors = {};
  for (const key of ["make", "model", "category"]) {
    const text = values[key].trim();
    if (!text) errors[key] = "Required";
    else if (text.length > 50) errors[key] = "50 characters max";
  }
  const price = Number(values.price);
  if (values.price === "" || !(price > 0)) errors.price = "Must be greater than 0";
  else if (!/^\d+(\.\d{1,2})?$/.test(values.price)) errors.price = "Up to 2 decimal places";
  const quantity = Number(values.quantity);
  if (values.quantity === "" || !Number.isInteger(quantity) || quantity < 0) {
    errors.quantity = "Whole number, 0 or more";
  }
  return errors;
}

export default function VehicleForm({ initial, submitLabel, onSubmit, onCancel }) {
  const [values, setValues] = useState(() =>
    initial
      ? { ...initial, price: String(initial.price), quantity: String(initial.quantity) }
      : BLANK,
  );
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (key) => (event) => setValues({ ...values, [key]: event.target.value });

  async function handleSubmit(event) {
    event.preventDefault();
    const found = validate(values);
    setErrors(found);
    setServerError("");
    if (Object.keys(found).length) return;

    setBusy(true);
    try {
      await onSubmit({
        make: values.make.trim(),
        model: values.model.trim(),
        category: values.category.trim(),
        price: Number(values.price),
        quantity: Number(values.quantity),
      });
      if (!initial) setValues(BLANK);
    } catch (error) {
      setServerError(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Field label="Make" value={values.make} onChange={update("make")} error={errors.make} />
        <Field label="Model" value={values.model} onChange={update("model")} error={errors.model} />
        <Field
          label="Category"
          value={values.category}
          onChange={update("category")}
          error={errors.category}
        />
      </div>
      <div className="grid grid-cols-2 gap-3 sm:max-w-md">
        <Field
          label="Price"
          type="number"
          min="0"
          step="0.01"
          value={values.price}
          onChange={update("price")}
          error={errors.price}
        />
        <Field
          label="Quantity"
          type="number"
          min="0"
          step="1"
          value={values.quantity}
          onChange={update("quantity")}
          error={errors.quantity}
        />
      </div>
      <Alert kind="error">{serverError}</Alert>
      <div className="flex flex-wrap gap-3">
        <Button type="submit" variant="red" busy={busy}>
          {submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" onClick={onCancel} disabled={busy}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
