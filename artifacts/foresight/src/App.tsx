import { Redirect, Route, Switch, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SessionProvider, useSession } from "@/lib/session";
import NotFound from "@/pages/not-found";
import LoginPage from "@/pages/login";
import SignupPage from "@/pages/signup";
import WaitingPage from "@/pages/waiting";
import ScanPage from "@/pages/scan";
import BrowsePage from "@/pages/browse";
import ShadowsPage from "@/pages/shadows";
import RosterPage from "@/pages/roster";
import TermsPage from "@/pages/terms";
import AuditPage from "@/pages/audit";
import AnalyticsPage from "@/pages/analytics";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-sm text-gray-600">Loading…</p>
    </div>
  );
}

function Routed() {
  const { status } = useSession();

  if (status === "loading") {
    return <LoadingScreen />;
  }

  if (status === "signedOut") {
    return (
      <Switch>
        <Route path="/login" component={LoginPage} />
        <Route path="/signup" component={SignupPage} />
        <Route>
          <Redirect to="/login" />
        </Route>
      </Switch>
    );
  }

  if (status === "unapproved") {
    return (
      <Switch>
        <Route path="/waiting" component={WaitingPage} />
        <Route>
          <Redirect to="/waiting" />
        </Route>
      </Switch>
    );
  }

  const isAdmin = status === "admin";

  return (
    <Switch>
      <Route path="/" component={ScanPage} />
      <Route path="/browse" component={BrowsePage} />
      <Route path="/shadows" component={ShadowsPage} />
      <Route path="/roster">{isAdmin ? <RosterPage /> : <NotFound />}</Route>
      <Route path="/terms">{isAdmin ? <TermsPage /> : <NotFound />}</Route>
      <Route path="/audit">{isAdmin ? <AuditPage /> : <NotFound />}</Route>
      <Route path="/analytics">{isAdmin ? <AnalyticsPage /> : <NotFound />}</Route>
      <Route path="/login">
        <Redirect to="/" />
      </Route>
      <Route path="/signup">
        <Redirect to="/" />
      </Route>
      <Route>
        <NotFound />
      </Route>
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <Routed />
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </SessionProvider>
    </QueryClientProvider>
  );
}

export default App;
