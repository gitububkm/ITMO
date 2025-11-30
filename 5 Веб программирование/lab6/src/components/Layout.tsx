import { ReactNode } from "react";

import "../App.css";
import { Header } from "./Header";

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => (
  <div className="app-shell">
    <Header />
    <main className="app-main">{children}</main>
  </div>
);


