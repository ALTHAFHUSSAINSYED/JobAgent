# Sprint 1.3: Frontend Dashboard Integration

This contract specifies the React-based orchestration frontend for JobPilot AI.

---

## 1. Goal
Initialize a Vite-powered React single page application with a high-fidelity dark-themed user interface that connects to backend APIs and visualizes diagnostic metrics, connectivity handshakes, and running configurations.

---

## 2. Directory Layout
```text
frontend/
├── index.html                   # Entry page template
├── src/
│   ├── main.jsx                 # Client entry point
│   ├── App.jsx                  # Main dashboard controller
│   ├── App.css                  # Vanilla CSS stylesheet containing design system
│   └── components/
│       ├── StatusCard.jsx       # Indicators for DB, Redis, etc.
│       └── LogsTerminal.jsx     # Debug logs viewer
└── package.json
```

---

## 3. Specifications

### 3.1 UI Design System (App.css)
- **Palette:** HSL custom dark mode (Primary dark: `#0b0f19`, Cards: `#151c2c`, Accent Green: `#00e676`, Accent Red: `#ff1744`, Slate Text: `#94a3b8`).
- **Aesthetics:** Subtle glow effects, glassmorphic card boundaries, and responsive grids.

### 3.2 Main Dashboard Panel (App.jsx)
- **State Management:** Polls `GET /api/v1/dashboard` every 5 seconds.
- **Service Monitor Cards:** Shows the following components:
  1. **Database:** Green when `connected`, Red otherwise.
  2. **Event Bus (Redis):** Green when `connected`, Red otherwise.
  3. **Browser Engine:** Green when `installed`, Red otherwise.
  4. **OpenRouter API:** Green when `ready`, Red otherwise.
- **Candidate Data Grid:** Renders loaded candidate data (Name, Email, Profile metrics).
- **Diagnostics Log terminal:** Fetches recent log outputs from backend diagnostics logs to show live execution updates.

### 3.3 Logs Terminal Component
- Styled as a developer shell console with a black background, monospace font, and toggle buttons to filter errors versus logs.

---

## 4. Acceptance Criteria
- Accessing `http://localhost:3000` loads the dark UI without errors.
- Disconnecting the backend container dynamically changes the UI cards to a Red "Offline" state.
- Loaded profile configurations are readable on the main console panel.
