"use client";

import React from "react";
import GeneratorExplorer from "@/components/GeneratorExplorer";
import SidebarNav from "@/components/SidebarNav";
import Toast from "@/components/Toast";

export default function GeneratorsPage() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <SidebarNav />
      <main className="flex-1 p-8">
        <div className="max-w-6xl mx-auto">
          <GeneratorExplorer />
        </div>
      </main>
      <Toast />
    </div>
  );
}
