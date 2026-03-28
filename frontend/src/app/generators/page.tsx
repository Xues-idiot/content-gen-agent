"use client";

import React from "react";
import GeneratorExplorer from "@/components/GeneratorExplorer";
import SidebarNav from "@/components/SidebarNav";
import { ToastProvider } from "@/components/Toast";

function GeneratorsContent() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <main className="lg:ml-72 pt-16 lg:pt-0 pb-20 lg:pb-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <GeneratorExplorer />
        </div>
      </main>
    </div>
  );
}

export default function GeneratorsPage() {
  return (
    <SidebarNav>
      <ToastProvider>
        <GeneratorsContent />
      </ToastProvider>
    </SidebarNav>
  );
}
