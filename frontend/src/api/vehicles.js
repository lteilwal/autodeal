import { request } from "./client";

export const listVehicles = () => request("/api/vehicles");

// filters: { make, model, category, min_price, max_price }; empty values are skipped.
export const searchVehicles = (filters) => request("/api/vehicles/search", { params: filters });

export const createVehicle = (vehicle) =>
  request("/api/vehicles", { method: "POST", body: vehicle });

export const updateVehicle = (id, vehicle) =>
  request(`/api/vehicles/${id}`, { method: "PUT", body: vehicle });

export const deleteVehicle = (id) => request(`/api/vehicles/${id}`, { method: "DELETE" });

export const purchaseVehicle = (id, quantity) =>
  request(`/api/vehicles/${id}/purchase`, { method: "POST", body: { quantity } });

export const restockVehicle = (id, quantity) =>
  request(`/api/vehicles/${id}/restock`, { method: "POST", body: { quantity } });
