"use client"

import React, { useRef } from 'react'
import Link from "next/link"
import dynamic from "next/dynamic"

const VBlockModel = dynamic(
  () => import("@/components/VBlockModel").then((mod) => mod.VBlockModel),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full w-full items-center justify-center text-sm text-slate-400 bg-[#f8fafc] rounded-2xl border border-slate-200">
        Loading 3D Canvas...
      </div>
    ),
  }
)

export default function VBlockPage() {
  const viewerRef = useRef<any>(null)

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 font-sans">
      
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-200 shadow-sm relative z-20">
        <h1 className="text-2xl font-semibold text-slate-800">
          บทที่ 1: การเขียนภาพไอโซเมตริก (Isometric Drawing)
        </h1>
        <Link 
          href="/" 
          className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors shadow-sm"
        >
          Back to Lessons
        </Link>
      </header>

      <main className="max-w-[1400px] mx-auto p-8 flex flex-col gap-6">
        
        {/* Info banner */}
        <div className="bg-[#ccfbf1] border border-[#99f6e4] rounded-xl p-5 shadow-sm text-teal-900">
          <h2 className="font-semibold text-teal-800 mb-2">Engineering Standard Alignment</h2>
          <p className="text-sm mb-1 text-teal-700">Standards: <span className="font-medium">ISO 5456 / ISO 128 (ISO 5456 for pictorial methods, ISO 128 for line conventions)</span></p>
          <p className="text-sm mb-3 text-teal-700">Focus: <span className="font-medium">Isometric (30°/30°) and Oblique (45°) pictorial construction</span></p>
          <p className="text-sm font-medium text-teal-800">Learning Outcome: นิสิตสามารถสร้างภาพ Isometric จากภาพฉายได้ตามมาตรฐาน ISO 5456-3</p>
        </div>

        {/* Main Workspace */}
        <div className="flex flex-col lg:flex-row gap-6 h-[720px] w-full">
          
          {/* Left Control Panel */}
          <div className="w-full lg:w-80 flex flex-col bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden flex-shrink-0 relative z-10">
            <div className="p-6 border-b border-slate-100">
              <h3 className="text-xl font-bold mb-2 text-slate-800">Interactive 3D Lesson</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Rotate with drag, zoom with scroll, and reset to the standard view.
              </p>
            </div>

            <div className="p-6 border-b border-slate-100">
              <span className="text-xs font-semibold text-slate-400 tracking-wider uppercase block mb-3">Lesson Selector</span>
              <div className="grid grid-cols-4 border border-blue-200 rounded-lg overflow-hidden shadow-sm">
                <button className="py-2.5 bg-blue-600 text-white font-medium text-sm transition-colors hover:bg-blue-700">Lesson 1</button>
                <button className="py-2.5 bg-white text-blue-600 font-medium text-sm border-l border-blue-200 hover:bg-blue-50 transition-colors">Lesson 2</button>
                <button className="py-2.5 bg-white text-blue-600 font-medium text-sm border-l border-blue-200 hover:bg-blue-50 transition-colors">Lesson 3</button>
                <button className="py-2.5 bg-white text-blue-600 font-medium text-sm border-l border-blue-200 hover:bg-blue-50 transition-colors">Lesson 4</button>
              </div>
            </div>

            <div className="p-6 flex-1 flex flex-col">
              <h4 className="font-bold text-slate-800 mb-1">Isometric Basics</h4>
              <p className="text-xs text-slate-500 mb-6">Cube construction using 30° axes.</p>

              <div className="flex flex-col gap-4 text-sm text-slate-700 font-medium mb-8">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-1 bg-[#ef4444] rounded-full shadow-sm"></div>
                  <span>Axes (X, Y, Z)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-1 bg-[#94a3b8] rounded-full shadow-sm"></div>
                  <span>Construction lines (thin)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-1.5 bg-[#1e293b] rounded-full shadow-sm"></div>
                  <span>Object edges (bold)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-1 bg-[#f97316] rounded-full shadow-sm"></div>
                  <span>30° isometric guide</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-5 h-1 bg-[#10b981] rounded-full shadow-sm"></div>
                  <span>45° oblique guide</span>
                </div>
              </div>

              <div className="mt-auto">
                <button 
                  onClick={() => viewerRef.current?.resetView()}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors shadow-md shadow-blue-600/20 active:scale-[0.98]"
                >
                  Reset View
                </button>
              </div>
            </div>
          </div>

          {/* Right 3D Viewer Canvas */}
          <div className="flex-1 w-full bg-white border border-slate-200 rounded-2xl shadow-sm p-2 lg:p-3 relative overflow-hidden">
            <VBlockModel ref={viewerRef} />
          </div>

        </div>
        
        {/* Footer info text */}
        <p className="text-sm font-medium text-slate-600 pt-2">
          นิสิตสามารถสร้างภาพ Isometric จากภาพฉายได้ตามมาตรฐาน ISO 5456-3
        </p>
      </main>
    </div>
  )
}
