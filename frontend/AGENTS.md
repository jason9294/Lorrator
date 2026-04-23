# AGENTS Instructions

## Environment

- Use `pnpm` as the package manager

## API Client

- API client code is located in `/src/services`
- All files in this directory are auto-generated
- To regenerate the API client, run:
  - `pnpm openapi-ts`

## Component Guidelines

### General Principles

- Components should focus on **UI logic (presentation logic)** only
- Avoid embedding **business logic** inside components
- Business logic should be placed in:
  - composables (`/src/composables`)
  - stores (e.g., Pinia)
  - service layer

### Component Responsibilities

✅ Allowed inside components:

- UI state (e.g., modal open/close, loading state)
- User interactions (click, input, focus, etc.)
- Local state and simple computed values
- Display formatting

❌ Avoid inside components:

- API calls and data fetching logic
- Complex business rules
- Cross-component shared logic

### Event Handling (emit)

- Use `emit` for **reusable UI components** (e.g., buttons, inputs)
- Do NOT overuse `emit` for page-level or container logic
- Page or container components can directly call composables or stores

## Component Structure

- Keep components **small and focused**
- Avoid overly large single-file components
- Split components when:
  - logic becomes complex
  - template becomes hard to read
  - reuse is possible

## UI Library

- The project uses `shadcn-vue`
- UI components are located in:
  - `/src/components/ui`
- Do NOT modify these files unless absolutely necessary

## Restrictions

- Do NOT manually modify any files in:
  - `/src/services/*`
- These files will be overwritten by code generation
