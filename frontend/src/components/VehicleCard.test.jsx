import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ApiError } from "../api/client";
import VehicleCard from "./VehicleCard";

const corolla = {
  id: 7,
  make: "Toyota",
  model: "Corolla",
  category: "Sedan",
  price: 22050,
  quantity: 3,
};

function renderCard(vehicle = corolla, purchase = vi.fn().mockResolvedValue({})) {
  const actions = { purchase, restock: vi.fn(), update: vi.fn(), remove: vi.fn() };
  render(<VehicleCard vehicle={vehicle} isAdmin={false} actions={actions} />);
  return { purchase, user: userEvent.setup() };
}

describe("VehicleCard buy confirmation", () => {
  it("asks for confirmation with the vehicle name and price before purchasing", async () => {
    const { purchase, user } = renderCard();

    await user.click(screen.getByRole("button", { name: "Buy" }));

    const dialog = screen.getByRole("dialog");
    expect(dialog.textContent).toContain("Toyota Corolla");
    expect(dialog.textContent).toContain("$22,050.00");
    expect(purchase).not.toHaveBeenCalled();
  });

  it("does not purchase when the dialog is cancelled", async () => {
    const { purchase, user } = renderCard();

    await user.click(screen.getByRole("button", { name: "Buy" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByRole("dialog")).toBeNull();
    expect(purchase).not.toHaveBeenCalled();
  });

  it("purchases the chosen quantity after confirmation and shows success", async () => {
    const { purchase, user } = renderCard();

    const qty = screen.getByRole("spinbutton");
    await user.clear(qty);
    await user.type(qty, "2");
    await user.click(screen.getByRole("button", { name: "Buy" }));
    expect(screen.getByRole("dialog").textContent).toContain("$44,100.00");
    await user.click(screen.getByRole("button", { name: "Confirm purchase" }));

    expect(purchase).toHaveBeenCalledExactlyOnceWith(7, 2);
    expect(screen.queryByRole("dialog")).toBeNull();
    expect((await screen.findByRole("status")).textContent).toBe("Purchased 2 × Toyota Corolla");
  });

  it("shows a clear message when stock ran out before confirming", async () => {
    const purchase = vi.fn().mockRejectedValue(new ApiError(409, "Insufficient stock"));
    const { user } = renderCard(corolla, purchase);

    await user.click(screen.getByRole("button", { name: "Buy" }));
    await user.click(screen.getByRole("button", { name: "Confirm purchase" }));

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Not enough stock left. The inventory has been refreshed.",
    );
  });

  it("disables buying when the vehicle is sold out", () => {
    renderCard({ ...corolla, quantity: 0 });

    expect(screen.getByRole("button", { name: "Sold out" }).disabled).toBe(true);
  });
});
