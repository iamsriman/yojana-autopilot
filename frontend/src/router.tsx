import { lazy, useCallback, useEffect, useSyncExternalStore } from "react";

const HomePage = lazy(() => import("./pages/HomePage"));
const ChatPage = lazy(() => import("./pages/ChatPage"));
const EligibilityPage = lazy(() => import("./pages/EligibilityPage"));
const ServicesPage = lazy(() => import("./pages/ServicesPage"));
const OfficesPage = lazy(() => import("./pages/OfficesPage"));
const AboutPage = lazy(() => import("./pages/AboutPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

export const routes = [
  { path: "/", label: "Home", element: HomePage, showInNav: true },
  { path: "/assistant", label: "AI Assistant", element: ChatPage, showInNav: true },
  { path: "/eligibility", label: "Eligibility", element: EligibilityPage, showInNav: true },
  { path: "/services", label: "Services", element: ServicesPage, showInNav: true },
  { path: "/offices", label: "Offices", element: OfficesPage, showInNav: true },
  { path: "/about", label: "About", element: AboutPage, showInNav: true },
] as const;

function subscribe(callback: () => void) {
  window.addEventListener("popstate", callback);
  window.addEventListener("yojana:navigate", callback);
  return () => {
    window.removeEventListener("popstate", callback);
    window.removeEventListener("yojana:navigate", callback);
  };
}

function getSnapshot() {
  return window.location.pathname;
}

export function useRoute() {
  const path = useSyncExternalStore(subscribe, getSnapshot, () => "/");

  const navigate = useCallback((nextPath: string) => {
    if (window.location.pathname !== nextPath) {
      window.history.pushState({}, "", nextPath);
      window.dispatchEvent(new Event("yojana:navigate"));
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    const handler = (event: MouseEvent) => {
      const target = event.target as HTMLElement | null;
      const anchor = target?.closest("a");
      if (!anchor) return;
      const href = anchor.getAttribute("href");
      if (!href?.startsWith("/")) return;
      event.preventDefault();
      navigate(href);
    };
    document.addEventListener("click", handler);
    return () => document.removeEventListener("click", handler);
  }, [navigate]);

  const match = routes.find((route) => route.path === path);
  return {
    path,
    navigate,
    Component: match?.element ?? NotFoundPage,
  };
}
