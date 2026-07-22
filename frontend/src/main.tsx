import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import "./styles/index.css";
import { AppShell } from "./components/layout/AppShell";
import { ToastProvider } from "./components/ui/Toast";
import { PageLoader } from "./components/ui/Loader";

const App = lazy(() => import("./App"));

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ToastProvider>
      <AppShell>
        <Suspense fallback={<PageLoader />}>
          <App />
        </Suspense>
      </AppShell>
    </ToastProvider>
  </React.StrictMode>,
);
