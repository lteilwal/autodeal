import { useCallback, useEffect, useState } from "react";

import * as vehiclesApi from "../api/vehicles";
import { useAuth } from "../context/AuthContext";
import SearchFilters, { EMPTY_FILTERS } from "./SearchFilters";
import VehicleCard from "./VehicleCard";
import VehicleForm from "./VehicleForm";
import { Alert, Button, Panel, Spinner } from "./ui";

const hasFilters = (filters) => Object.values(filters).some((value) => value !== "");

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [vehicles, setVehicles] = useState([]);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);

  // A quiet reload keeps the cards on screen so their success/error messages stay visible.
  const load = useCallback(async (activeFilters, { quiet = false } = {}) => {
    if (!quiet) setLoading(true);
    setError("");
    try {
      const result = hasFilters(activeFilters)
        ? await vehiclesApi.searchVehicles(activeFilters)
        : await vehiclesApi.listVehicles();
      setVehicles(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(filters);
  }, [load, filters]);

  // After any change, reload so stock and search results stay accurate.
  // A failed purchase (e.g. someone else bought the last one) reloads too.
  const refreshAfter = (call) => async (...args) => {
    try {
      await call(...args);
    } finally {
      load(filters, { quiet: true });
    }
  };

  const actions = {
    purchase: refreshAfter(vehiclesApi.purchaseVehicle),
    restock: refreshAfter(vehiclesApi.restockVehicle),
    update: refreshAfter(vehiclesApi.updateVehicle),
    remove: refreshAfter(vehiclesApi.deleteVehicle),
  };

  async function handleCreate(values) {
    await vehiclesApi.createVehicle(values);
    setShowAddForm(false);
    load(filters, { quiet: true });
  }

  return (
    <div className="min-h-screen">
      <header className="chrome sticky top-0 z-10 border-x-0 border-t-0">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <span className="emblem chrome">AutoDeal</span>
          <div className="flex items-center gap-3">
            <div className="text-right text-sm leading-tight">
              <div className="font-semibold break-all">{user.email}</div>
              <div className="text-xs font-bold tracking-widest text-teal-dark uppercase">
                {user.is_admin ? "Administrator" : "Customer"}
              </div>
            </div>
            <Button onClick={() => logout()}>Log out</Button>
          </div>
        </div>
        <div className="mx-auto max-w-6xl px-4 pb-3">
          <div className="grille" />
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-8">
        <SearchFilters onSearch={setFilters} busy={loading} />

        {user.is_admin && (
          <Panel title="Add a vehicle">
            {showAddForm ? (
              <VehicleForm
                submitLabel="Add vehicle"
                onSubmit={handleCreate}
                onCancel={() => setShowAddForm(false)}
              />
            ) : (
              <Button variant="teal" onClick={() => setShowAddForm(true)}>
                New vehicle
              </Button>
            )}
          </Panel>
        )}

        <section aria-labelledby="inventory-heading" className="flex flex-col gap-4">
          <h2
            id="inventory-heading"
            className="font-display text-2xl tracking-wide text-cream drop-shadow"
          >
            {hasFilters(filters) ? "Search results" : "Showroom"}
            {!loading && <span className="ml-2 text-base opacity-80">({vehicles.length})</span>}
          </h2>

          {error && (
            <Panel>
              <Alert kind="error">{error}</Alert>
              <Button className="mt-3" onClick={() => load(filters)}>
                Try again
              </Button>
            </Panel>
          )}

          {loading ? (
            <Spinner label="Loading inventory…" />
          ) : (
            !error &&
            (vehicles.length === 0 ? (
              <Panel>
                <p className="text-center font-semibold">
                  {hasFilters(filters)
                    ? "No vehicles match those filters."
                    : "The showroom is empty."}
                </p>
              </Panel>
            ) : (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {vehicles.map((vehicle) => (
                  <VehicleCard
                    key={vehicle.id}
                    vehicle={vehicle}
                    isAdmin={user.is_admin}
                    actions={actions}
                  />
                ))}
              </div>
            ))
          )}
        </section>
      </main>
    </div>
  );
}
