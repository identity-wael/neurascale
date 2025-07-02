'use client'

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { BrainCircuit, Cloud, Zap, Menu } from "lucide-react";

export default function Home() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
      <div className="flex flex-col min-h-screen bg-black text-white">
        <header className="fixed top-0 left-0 right-0 z-50 px-4 lg:px-6 py-4">
          <div className="container mx-auto flex items-center justify-between">
            <a className="flex items-center justify-center" href="#">
              <span className="sr-only">NEURASCALE</span>
              <span className="font-black text-2xl tracking-wider" style={{ fontFamily: 'Proxima Nova, sans-serif' }}>
              <span className="text-white">NEURA</span>
              <span className="text-gray-400">SCALE</span>
            </span>
            </a>
            <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="lg:hidden">
              <Menu className="w-6 h-6" />
            </button>
            <nav className={`${isMenuOpen ? 'flex' : 'hidden'} lg:flex absolute lg:relative top-full left-0 right-0 bg-black lg:bg-transparent flex-col lg:flex-row items-center gap-4 p-4 lg:p-0`}>
              <a className="text-sm font-medium hover:text-gray-300 transition-colors" href="#">
                About
              </a>
              <a className="text-sm font-medium hover:text-gray-300 transition-colors" href="/login">
                Sign in
              </a>
              <a href="/signup">
                <Button variant="outline" className="border-white text-white hover:bg-white hover:text-black transition-colors">
                  Sign up
                </Button>
              </a>
            </nav>
          </div>
        </header>

        <main className="flex-1 pt-20">
          <section className="relative overflow-hidden w-full py-24 md:py-32 lg:py-48">
            <div className="relative z-10 container mx-auto px-4 md:px-6">
              <div className="flex flex-col items-center space-y-4 text-center">
                <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl max-w-3xl mx-auto leading-tight">
                  Unleash the Power of Neural Data Cloud
                </h1>
                <p className="mx-auto max-w-[700px] text-gray-400 md:text-xl/relaxed lg:text-2xl/relaxed">
                  NEURASCALE provides a cutting-edge platform for storing, processing, and analyzing neural data at scale.
                </p>
                <button className="rounded px-6 py-3 text-lg mt-8 bg-white text-black hover:bg-gray-200 transition-colors">
                  Explore Our Technology
                </button>
              </div>
            </div>
          </section>
          <section className="w-full py-24 md:py-32">
            <div className="container mx-auto px-4 md:px-6">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12">
                Key Features
              </h2>
              <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
                <Card className="bg-gray-900 border-gray-800">
                  <CardContent className="pt-8">
                    <BrainCircuit className="w-12 h-12 mb-4 text-blue-400" />
                    <h3 className="text-xl font-bold mb-2">Advanced Neural Processing</h3>
                    <p className="text-gray-400">Leverage our state-of-the-art algorithms for efficient neural data processing and analysis.</p>
                  </CardContent>
                </Card>
                <Card className="bg-gray-900 border-gray-800">
                  <CardContent className="pt-8">
                    <Cloud className="w-12 h-12 mb-4 text-blue-400" />
                    <h3 className="text-xl font-bold mb-2">Scalable Cloud Infrastructure</h3>
                    <p className="text-gray-400">Store and manage petabytes of neural data with our highly scalable cloud infrastructure.</p>
                  </CardContent>
                </Card>
                <Card className="bg-gray-900 border-gray-800">
                  <CardContent className="pt-8">
                    <Zap className="w-12 h-12 mb-4 text-blue-400" />
                    <h3 className="text-xl font-bold mb-2">Real-time Analytics</h3>
                    <p className="text-gray-400">Gain insights from your neural data in real-time with our powerful analytics tools.</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>
          <section className="w-full py-24 md:py-32 bg-gray-900">
            <div className="container mx-auto px-4 md:px-6">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center mb-12">
                What Our Clients Say
              </h2>
              <div className="grid gap-8 md:grid-cols-2">
                <Card className="bg-black border-gray-800">
                  <CardContent className="pt-8">
                    <p className="text-lg mb-4 text-gray-300">&quot;NEURASCALE has revolutionized how we handle our neural data. Their platform is incredibly powerful and user-friendly.&quot;</p>
                    <p className="font-semibold text-white">Dr. Jane Smith, Neuroscience Research Institute</p>
                  </CardContent>
                </Card>
                <Card className="bg-black border-gray-800">
                  <CardContent className="pt-8">
                    <p className="text-lg mb-4 text-gray-300">&quot;The scalability and real-time analytics capabilities of NEURASCALE have significantly accelerated our research progress.&quot;</p>
                    <p className="font-semibold text-white">Prof. John Doe, AI Research Lab</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </section>
          <section className="w-full py-24 md:py-32">
            <div className="container mx-auto px-4 md:px-6">
              <div className="flex flex-col items-center space-y-4 text-center">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                  Ready to Scale Your Neural Data?
                </h2>
                <p className="mx-auto max-w-[600px] text-gray-400 md:text-xl/relaxed lg:text-2xl/relaxed">
                  Join the leading researchers and institutions already benefiting from NEURASCALE&apos;s advanced platform.
                </p>
                <button className="rounded px-6 py-3 text-lg mt-8 bg-white text-black hover:bg-gray-200 transition-colors">
                  Start Free Trial
                </button>
              </div>
            </div>
          </section>
        </main>

        <footer className="py-6 w-full border-t border-gray-800">
          <div className="container mx-auto px-4 md:px-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-sm text-gray-400">&copy; 2023 NEURASCALE. All rights reserved.</p>
              <nav className="flex gap-4">
                <a className="text-sm text-gray-400 hover:text-white transition-colors" href="#">
                  Terms of Service
                </a>
                <a className="text-sm text-gray-400 hover:text-white transition-colors" href="#">
                  Privacy Policy
                </a>
                <a className="text-sm text-gray-400 hover:text-white transition-colors" href="#">
                  Contact
                </a>
              </nav>
            </div>
          </div>
        </footer>
      </div>
  );
}
