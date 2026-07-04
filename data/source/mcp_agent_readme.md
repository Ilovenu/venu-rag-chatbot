# automationexercise-e2e-framework

Production-style E2E test automation framework for [automationexercise.com](https://automationexercise.com) — **Playwright + TypeScript**, Page Object Model architecture, genuine hybrid API/UI testing, cross-browser CI/CD with Allure reporting.

[![E2E Tests](https://github.com/Ilovenu/MCP_Agent/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/Ilovenu/MCP_Agent/actions/workflows/e2e-tests.yml)
![Playwright](https://img.shields.io/badge/Playwright-1.61-2EAD33?logo=playwright&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
[![Allure Report](https://img.shields.io/badge/Allure-Live%20Report-orange)](https://ilovenu.github.io/MCP_Agent/)

**[View the latest live test report →](https://ilovenu.github.io/MCP_Agent/)**

## Why this project

automationexercise.com was chosen deliberately over more common demo sites (e.g. saucedemo.com): it exposes **both** a real browsable UI and a documented public REST API, which is what makes genuine hybrid API+UI testing possible instead of UI-only scripts.

## What this demonstrates

- **Page Object Model** — pages hold locators and business-readable actions; assertions stay in specs
- **Custom Playwright fixtures** — dependency-injected page objects, an `ApiClient`, and a `createdApiUser` fixture that owns account setup/teardown lifecycle
- **API testing** — full coverage of the site's REST endpoints, including documented error contracts (missing params, unsupported HTTP methods)
- **Hybrid API+UI testing** — API creates state that the UI verifies, and vice versa, including cross-layer field-consistency assertions
- **Data-driven testing** — search scenarios parametrized from a shared JSON fixture, reused by both the UI and API suites
- **Cross-browser matrix** — Chromium, Firefox, WebKit, run independently in CI
- **CI/CD** — GitHub Actions matrix with per-project pass/fail, artifact upload, and a published live Allure report
- **Reliability engineering** — the target site serves live Google ad interstitials that reliably break `networkidle` waits and intercept clicks; this framework blocks ad domains at the network layer (see `src/fixtures/test-options.ts`) instead of papering over it with blind retries
- **Reporting/observability** — HTML report locally, Allure report in CI with screenshots/video/trace on failure

## Tech stack

| Layer       | Choice                                                                    |
| ----------- | ------------------------------------------------------------------------- |
| Test runner | `@playwright/test`                                                        |
| Language    | TypeScript 5                                                              |
| Test data   | `@faker-js/faker`                                                         |
| Lint/format | ESLint (`typescript-eslint`, `eslint-plugin-playwright`) + Prettier       |
| Reporting   | Playwright HTML reporter (local) + Allure (CI, published to GitHub Pages) |
| CI/CD       | GitHub Actions                                                            |

## Project structure

```
src/
├── pages/          # Page Object Model — one class per page
├── components/      # Reusable widgets shared across pages (header, cart modal, product card)
├── api/              # ApiClient, endpoint constants, response/user/product models
├── fixtures/         # Custom Playwright fixtures + JSON test data
└── utils/             # env config, faker-based test data generation
tests/
├── ui/               # UI specs, grouped by feature (auth, products, cart, checkout, contact)
├── api/               # API specs, one file per resource + a negative-method contract suite
└── hybrid/            # API-creates/UI-verifies and UI-creates/API-verifies specs
.github/workflows/    # CI: cross-browser matrix + Allure publish to GitHub Pages
```

## Getting started

```bash
npm ci
npx playwright install
cp .env.example .env   # optional — defaults already point at automationexercise.com

npm test               # run everything
npm run test:smoke     # @smoke only
npm run test:ui        # UI suites
npm run test:api       # API suites
npm run test:hybrid    # hybrid suites
npm run report         # open the last local HTML report
```

## CI/CD

Every push and PR runs a GitHub Actions matrix across `chromium`, `firefox`, `webkit`, `api`, and `hybrid-chromium` as independent jobs (`fail-fast: false`, so one browser's flake doesn't hide the others' results). Each job uploads its HTML report and Allure results as build artifacts; a final job merges the Allure results across all jobs and publishes history to GitHub Pages, so the live report link above always reflects the latest run on `main`.

## Roadmap

- Nightly scheduled run with Allure trend history
- Visual regression on the home page carousel
- Accessibility smoke test via `@axe-core/playwright`

## License

MIT
