# Test Report

Results recorded from the latest local run on **2026-10-25 13:29 (UTC+05:30)**, Windows 11.
The output blocks below are copied unchanged from the terminal (only ANSI colour codes removed).

## Summary

| Suite | Command | Result |
|---|---|---|
| Backend (pytest, real PostgreSQL test database) | `.venv/Scripts/python -m pytest -v` | **120 passed**, 0 failed |
| Frontend (Vitest + React Testing Library) | `npx vitest run --reporter=verbose` (in `frontend/`) | **5 passed**, 0 failed |
| Frontend production build | `npm run build` (in `frontend/`) | **Succeeded** |

Environment: Python 3.14.2, PostgreSQL 18.6, Node 24.16.0, npm 11.13.0.

### Backend tests per file

| File | Tests |
|---|---|
| `backend/tests/test_api_flow.py` | 1 |
| `backend/tests/test_auth.py` | 34 |
| `backend/tests/test_database.py` | 1 |
| `backend/tests/test_health.py` | 1 |
| `backend/tests/test_seed_vehicles.py` | 4 |
| `backend/tests/test_setup.py` | 5 |
| `backend/tests/test_vehicles.py` | 15 |
| `backend/tests/test_vehicles_inventory.py` | 23 |
| `backend/tests/test_vehicles_list_search.py` | 16 |
| `backend/tests/test_vehicles_update_delete.py` | 20 |

## Backend: `pytest -v`

```text
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.7.0 -- C:\Comp\Projects\Car Dealership Inventory\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Comp\Projects\Car Dealership Inventory
configfile: pyproject.toml
testpaths: backend/tests
plugins: anyio-4.15.1
collecting ... collected 120 items

backend/tests/test_api_flow.py::test_full_api_flow PASSED                [  0%]
backend/tests/test_auth.py::test_hash_password_does_not_return_plain_text PASSED [  1%]
backend/tests/test_auth.py::test_hash_password_is_salted PASSED          [  2%]
backend/tests/test_auth.py::test_verify_password_accepts_correct_and_rejects_wrong_password PASSED [  3%]
backend/tests/test_auth.py::test_register_returns_201_with_user_and_no_password PASSED [  4%]
backend/tests/test_auth.py::test_register_stores_hashed_password PASSED  [  5%]
backend/tests/test_auth.py::test_register_cannot_grant_admin PASSED      [  5%]
backend/tests/test_auth.py::test_register_duplicate_email_returns_409 PASSED [  6%]
backend/tests/test_auth.py::test_register_invalid_input_returns_422[payload0] PASSED [  7%]
backend/tests/test_auth.py::test_register_invalid_input_returns_422[payload1] PASSED [  8%]
backend/tests/test_auth.py::test_register_invalid_input_returns_422[payload2] PASSED [  9%]
backend/tests/test_auth.py::test_register_invalid_input_returns_422[payload3] PASSED [ 10%]
backend/tests/test_auth.py::test_login_returns_bearer_token_for_user PASSED [ 10%]
backend/tests/test_auth.py::test_registered_user_can_log_in_and_use_token PASSED [ 11%]
backend/tests/test_auth.py::test_login_with_incorrect_credentials_returns_401[credentials0] PASSED [ 12%]
backend/tests/test_auth.py::test_login_with_incorrect_credentials_returns_401[credentials1] PASSED [ 13%]
backend/tests/test_auth.py::test_protected_routes_without_token_return_401[post-/api/vehicles] PASSED [ 14%]
backend/tests/test_auth.py::test_protected_routes_without_token_return_401[get-/api/vehicles] PASSED [ 15%]
backend/tests/test_auth.py::test_protected_routes_without_token_return_401[get-/api/vehicles/search] PASSED [ 15%]
backend/tests/test_auth.py::test_protected_routes_without_token_return_401[put-/api/vehicles/1] PASSED [ 16%]
backend/tests/test_auth.py::test_protected_routes_without_token_return_401[delete-/api/vehicles/1] PASSED [ 17%]
backend/tests/test_auth.py::test_invalid_token_returns_401[garbage] PASSED [ 18%]
backend/tests/test_auth.py::test_invalid_token_returns_401[expired] PASSED [ 19%]
backend/tests/test_auth.py::test_invalid_token_returns_401[wrong-secret] PASSED [ 20%]
backend/tests/test_auth.py::test_invalid_token_returns_401[unknown-user] PASSED [ 20%]
backend/tests/test_auth.py::test_invalid_token_returns_401[wrong-scheme] PASSED [ 21%]
backend/tests/test_auth.py::test_regular_user_can_access_protected_route PASSED [ 22%]
backend/tests/test_auth.py::test_regular_user_cannot_access_admin_route PASSED [ 23%]
backend/tests/test_auth.py::test_health_does_not_require_token PASSED    [ 24%]
backend/tests/test_auth.py::test_register_password_over_72_bytes_returns_422 PASSED [ 25%]
backend/tests/test_auth.py::test_login_with_overlong_password_returns_401 PASSED [ 25%]
backend/tests/test_auth.py::test_me_returns_regular_user PASSED          [ 26%]
backend/tests/test_auth.py::test_me_returns_admin_flag_for_admin PASSED  [ 27%]
backend/tests/test_auth.py::test_me_without_token_returns_401 PASSED     [ 28%]
backend/tests/test_auth.py::test_me_with_invalid_token_returns_401 PASSED [ 29%]
backend/tests/test_database.py::test_db_session_uses_test_database PASSED [ 30%]
backend/tests/test_health.py::test_health_returns_ok PASSED              [ 30%]
backend/tests/test_seed_vehicles.py::test_sample_data_is_varied_and_includes_sold_out_cars PASSED [ 31%]
backend/tests/test_seed_vehicles.py::test_seed_inserts_all_samples_with_generated_ids PASSED [ 32%]
backend/tests/test_seed_vehicles.py::test_rerunning_seed_does_not_duplicate PASSED [ 33%]
backend/tests/test_seed_vehicles.py::test_seed_keeps_existing_inventory_untouched PASSED [ 34%]
backend/tests/test_setup.py::test_init_db_creates_tables_with_constraints PASSED [ 35%]
backend/tests/test_setup.py::test_init_db_keeps_existing_data PASSED     [ 35%]
backend/tests/test_setup.py::test_app_startup_initializes_database PASSED [ 36%]
backend/tests/test_setup.py::test_cors_preflight_allows_frontend_origin_with_auth_header PASSED [ 37%]
backend/tests/test_setup.py::test_cors_rejects_unknown_origin PASSED     [ 38%]
backend/tests/test_vehicles.py::test_create_vehicle_returns_201_with_created_vehicle PASSED [ 39%]
backend/tests/test_vehicles.py::test_create_vehicle_persists_to_database PASSED [ 40%]
backend/tests/test_vehicles.py::test_create_vehicle_assigns_unique_ids PASSED [ 40%]
backend/tests/test_vehicles.py::test_create_vehicle_missing_field_returns_422[make] PASSED [ 41%]
backend/tests/test_vehicles.py::test_create_vehicle_missing_field_returns_422[model] PASSED [ 42%]
backend/tests/test_vehicles.py::test_create_vehicle_missing_field_returns_422[category] PASSED [ 43%]
backend/tests/test_vehicles.py::test_create_vehicle_missing_field_returns_422[price] PASSED [ 44%]
backend/tests/test_vehicles.py::test_create_vehicle_missing_field_returns_422[quantity] PASSED [ 45%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[make-] PASSED [ 45%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[model-] PASSED [ 46%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[category-] PASSED [ 47%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[price-0] PASSED [ 48%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[price--1] PASSED [ 49%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[quantity--1] PASSED [ 50%]
backend/tests/test_vehicles.py::test_create_vehicle_invalid_value_returns_422[quantity-1.5] PASSED [ 50%]
backend/tests/test_vehicles_inventory.py::test_purchase_decreases_quantity PASSED [ 51%]
backend/tests/test_vehicles_inventory.py::test_purchase_entire_stock_leaves_zero PASSED [ 52%]
backend/tests/test_vehicles_inventory.py::test_purchase_sold_out_vehicle_returns_409 PASSED [ 53%]
backend/tests/test_vehicles_inventory.py::test_purchase_more_than_in_stock_returns_409 PASSED [ 54%]
backend/tests/test_vehicles_inventory.py::test_purchase_invalid_quantity_returns_422[payload0] PASSED [ 55%]
backend/tests/test_vehicles_inventory.py::test_purchase_invalid_quantity_returns_422[payload1] PASSED [ 55%]
backend/tests/test_vehicles_inventory.py::test_purchase_invalid_quantity_returns_422[payload2] PASSED [ 56%]
backend/tests/test_vehicles_inventory.py::test_purchase_invalid_quantity_returns_422[payload3] PASSED [ 57%]
backend/tests/test_vehicles_inventory.py::test_purchase_invalid_quantity_returns_422[payload4] PASSED [ 58%]
backend/tests/test_vehicles_inventory.py::test_purchase_missing_vehicle_returns_404 PASSED [ 59%]
backend/tests/test_vehicles_inventory.py::test_admin_can_purchase PASSED [ 60%]
backend/tests/test_vehicles_inventory.py::test_unauthenticated_purchase_returns_401 PASSED [ 60%]
backend/tests/test_vehicles_inventory.py::test_admin_restock_increases_quantity PASSED [ 61%]
backend/tests/test_vehicles_inventory.py::test_admin_can_restock_sold_out_vehicle PASSED [ 62%]
backend/tests/test_vehicles_inventory.py::test_restock_invalid_quantity_returns_422[payload0] PASSED [ 63%]
backend/tests/test_vehicles_inventory.py::test_restock_invalid_quantity_returns_422[payload1] PASSED [ 64%]
backend/tests/test_vehicles_inventory.py::test_restock_invalid_quantity_returns_422[payload2] PASSED [ 65%]
backend/tests/test_vehicles_inventory.py::test_restock_invalid_quantity_returns_422[payload3] PASSED [ 65%]
backend/tests/test_vehicles_inventory.py::test_restock_invalid_quantity_returns_422[payload4] PASSED [ 66%]
backend/tests/test_vehicles_inventory.py::test_restock_missing_vehicle_returns_404 PASSED [ 67%]
backend/tests/test_vehicles_inventory.py::test_regular_user_cannot_restock PASSED [ 68%]
backend/tests/test_vehicles_inventory.py::test_unauthenticated_restock_returns_401 PASSED [ 69%]
backend/tests/test_vehicles_inventory.py::test_database_rejects_negative_quantity PASSED [ 70%]
backend/tests/test_vehicles_list_search.py::test_list_vehicles_empty_returns_empty_list PASSED [ 70%]
backend/tests/test_vehicles_list_search.py::test_list_vehicles_returns_all_vehicles_ordered_by_id PASSED [ 71%]
backend/tests/test_vehicles_list_search.py::test_search_by_single_filter[params0-expected_models0] PASSED [ 72%]
backend/tests/test_vehicles_list_search.py::test_search_by_single_filter[params1-expected_models1] PASSED [ 73%]
backend/tests/test_vehicles_list_search.py::test_search_by_single_filter[params2-expected_models2] PASSED [ 74%]
backend/tests/test_vehicles_list_search.py::test_search_by_single_filter[params3-expected_models3] PASSED [ 75%]
backend/tests/test_vehicles_list_search.py::test_search_by_single_filter[params4-expected_models4] PASSED [ 75%]
backend/tests/test_vehicles_list_search.py::test_search_by_single_filter[params5-expected_models5] PASSED [ 76%]
backend/tests/test_vehicles_list_search.py::test_search_with_combined_filters_matches_all_of_them PASSED [ 77%]
backend/tests/test_vehicles_list_search.py::test_search_with_no_filters_returns_all_vehicles PASSED [ 78%]
backend/tests/test_vehicles_list_search.py::test_search_with_no_matches_returns_empty_list PASSED [ 79%]
backend/tests/test_vehicles_list_search.py::test_search_min_price_greater_than_max_price_returns_422 PASSED [ 80%]
backend/tests/test_vehicles_list_search.py::test_search_invalid_price_returns_422[params0] PASSED [ 80%]
backend/tests/test_vehicles_list_search.py::test_search_invalid_price_returns_422[params1] PASSED [ 81%]
backend/tests/test_vehicles_list_search.py::test_search_invalid_price_returns_422[params2] PASSED [ 82%]
backend/tests/test_vehicles_list_search.py::test_search_invalid_price_returns_422[params3] PASSED [ 83%]
backend/tests/test_vehicles_update_delete.py::test_update_vehicle_returns_200_with_updated_vehicle PASSED [ 84%]
backend/tests/test_vehicles_update_delete.py::test_update_vehicle_persists_to_database PASSED [ 85%]
backend/tests/test_vehicles_update_delete.py::test_update_missing_vehicle_returns_404 PASSED [ 85%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[make-] PASSED [ 86%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[model-] PASSED [ 87%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[category-] PASSED [ 88%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[price-0] PASSED [ 89%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[price--1] PASSED [ 90%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[quantity--1] PASSED [ 90%]
backend/tests/test_vehicles_update_delete.py::test_update_with_invalid_value_returns_422_and_leaves_vehicle_unchanged[quantity-1.5] PASSED [ 91%]
backend/tests/test_vehicles_update_delete.py::test_update_with_missing_field_returns_422[make] PASSED [ 92%]
backend/tests/test_vehicles_update_delete.py::test_update_with_missing_field_returns_422[model] PASSED [ 93%]
backend/tests/test_vehicles_update_delete.py::test_update_with_missing_field_returns_422[category] PASSED [ 94%]
backend/tests/test_vehicles_update_delete.py::test_update_with_missing_field_returns_422[price] PASSED [ 95%]
backend/tests/test_vehicles_update_delete.py::test_update_with_missing_field_returns_422[quantity] PASSED [ 95%]
backend/tests/test_vehicles_update_delete.py::test_admin_can_delete_vehicle PASSED [ 96%]
backend/tests/test_vehicles_update_delete.py::test_deleted_vehicle_no_longer_listed_or_deletable PASSED [ 97%]
backend/tests/test_vehicles_update_delete.py::test_delete_missing_vehicle_returns_404 PASSED [ 98%]
backend/tests/test_vehicles_update_delete.py::test_non_admin_cannot_delete_vehicle PASSED [ 99%]
backend/tests/test_vehicles_update_delete.py::test_unauthenticated_user_cannot_delete_vehicle PASSED [100%]

============================ 120 passed in 17.79s =============================
```

## Frontend: `vitest run --reporter=verbose`

```text

 RUN  v5.0.5 C:/Comp/Projects/Car Dealership Inventory/frontend

 ✓ src/components/VehicleCard.test.jsx > VehicleCard buy confirmation > asks for confirmation with the vehicle name and price before purchasing 308ms
 ✓ src/components/VehicleCard.test.jsx > VehicleCard buy confirmation > does not purchase when the dialog is cancelled 138ms
 ✓ src/components/VehicleCard.test.jsx > VehicleCard buy confirmation > purchases the chosen quantity after confirmation and shows success 281ms
 ✓ src/components/VehicleCard.test.jsx > VehicleCard buy confirmation > shows a clear message when stock ran out before confirming 141ms
 ✓ src/components/VehicleCard.test.jsx > VehicleCard buy confirmation > disables buying when the vehicle is sold out 16ms

 Test Files  1 passed (1)
      Tests  5 passed (5)
   Start at  13:30:08
   Duration  5.19s (environment 64%, tests 19%, import 15%, transform 2%, worker 1%)

```

## Frontend: `npm run build`

```text

> autodeal-frontend@0.1.0 build
> vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 26 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.68 kB │ gzip:  0.37 kB
dist/assets/index-DlAxnbzU.css   17.51 kB │ gzip:  4.52 kB
dist/assets/index-C6Il493i.js   236.20 kB │ gzip: 73.64 kB

✓ built in 579ms
```
