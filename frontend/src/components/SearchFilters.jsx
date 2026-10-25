import { useState } from "react";

import { Alert, Button, Field, Panel } from "./ui";

export const EMPTY_FILTERS = { make: "", model: "", category: "", min_price: "", max_price: "" };

function validate({ min_price, max_price }) {
  const min = min_price === "" ? null : Number(min_price);
  const max = max_price === "" ? null : Number(max_price);
  if ((min !== null && min < 0) || (max !== null && max < 0)) return "Prices can't be negative";
  if (min !== null && max !== null && min > max) return "Min price must not exceed max price";
  return "";
}

export default function SearchFilters({ onSearch, busy }) {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [error, setError] = useState("");

  const update = (key) => (event) => setFilters({ ...filters, [key]: event.target.value });

  function handleSubmit(event) {
    event.preventDefault();
    const problem = validate(filters);
    setError(problem);
    if (!problem) onSearch(filters);
  }

  function handleReset() {
    setFilters(EMPTY_FILTERS);
    setError("");
    onSearch(EMPTY_FILTERS);
  }

  return (
    <Panel title="Find a vehicle">
      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <Field label="Make" value={filters.make} onChange={update("make")} placeholder="Toyota" />
          <Field label="Model" value={filters.model} onChange={update("model")} placeholder="Corolla" />
          <Field
            label="Category"
            value={filters.category}
            onChange={update("category")}
            placeholder="Sedan"
          />
        </div>
        <div className="grid grid-cols-2 gap-3 sm:max-w-md">
          <Field
            label="Min price"
            type="number"
            min="0"
            value={filters.min_price}
            onChange={update("min_price")}
          />
          <Field
            label="Max price"
            type="number"
            min="0"
            value={filters.max_price}
            onChange={update("max_price")}
          />
        </div>
        <Alert kind="error">{error}</Alert>
        <div className="flex flex-wrap gap-3">
          <Button type="submit" variant="teal" disabled={busy}>
            Search
          </Button>
          <Button type="button" onClick={handleReset} disabled={busy}>
            Reset
          </Button>
        </div>
      </form>
    </Panel>
  );
}
