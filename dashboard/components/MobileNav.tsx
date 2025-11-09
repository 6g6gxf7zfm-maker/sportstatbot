'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { signOut } from 'next-auth/react';
import {
  Menu,
  X,
  LayoutDashboard,
  PlayCircle,
  FileText,
  LogOut,
  Trophy,
  Target,
  Star,
  Zap,
  Circle,
} from 'lucide-react';

const leagues = [
  { name: 'NFL', icon: Trophy },
  { name: 'NBA', icon: Target },
  { name: 'MLB', icon: Star },
  { name: 'NHL', icon: Zap },
  { name: 'MLS', icon: Circle },
];

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Jobs', href: '/jobs', icon: PlayCircle },
  { name: 'Exports', href: '/exports', icon: FileText },
];

export default function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const closeSidebar = () => setIsOpen(false);

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4 z-40">
        <h1 className="text-xl font-bold text-white">Sports Intel</h1>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 text-white hover:bg-gray-800 rounded-md transition-colors"
        >
          {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Sidebar Overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40 mt-16"
          onClick={closeSidebar}
        />
      )}

      {/* Mobile Sidebar */}
      <div
        className={`lg:hidden fixed top-16 left-0 bottom-0 w-64 bg-gray-900 border-r border-gray-800 z-50 transform transition-transform duration-200 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <nav className="flex-1 px-4 py-6 space-y-8 overflow-y-auto">
          {/* Main Navigation */}
          <div>
            <h2 className="px-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Navigation
            </h2>
            <div className="mt-3 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={closeSidebar}
                    className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActive
                        ? 'bg-gray-800 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Leagues */}
          <div>
            <h2 className="px-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Leagues
            </h2>
            <div className="mt-3 space-y-1">
              {leagues.map((league) => {
                const Icon = league.icon;
                return (
                  <Link
                    key={league.name}
                    href={`/dashboard?league=${league.name}`}
                    onClick={closeSidebar}
                    className="flex items-center px-3 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {league.name}
                  </Link>
                );
              })}
            </div>
          </div>
        </nav>

        {/* Sign Out */}
        <div className="p-4 border-t border-gray-800">
          <button
            onClick={() => {
              closeSidebar();
              signOut({ callbackUrl: '/auth/signin' });
            }}
            className="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
          >
            <LogOut className="mr-3 h-5 w-5" />
            Sign Out
          </button>
        </div>
      </div>
    </>
  );
}
