import React from "react";
import { Outlet } from "react-router-dom";
import Header from "../ui/Header";

const AppLayout = () => {
  return (
    <div className="min-vh-100 bg-light">
      <Header />
      <main className="container py-4">
        <Outlet />
      </main>
    </div>
  );
};

export default AppLayout;
