'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { signOut } from 'next-auth/react';
import {
  LayoutDashboard,
  PlayCircle,
  FileText,
  LogOut,
  Football,
  Basketball,
  BaseballBat,
  Hockey,
  Volleyball,
} from 'lucide-react';

const leagues = [
  { name: 'NFL', icon: Football },
  { name: 'NBA', icon: Basketball },
  { name: 'MLB', icon: BaseballBat },
  { name: 'NHL', icon: Hockey },
  { name: 'MLS', icon: Volleyball },
];

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Jobs', href: '/jobs', icon: PlayCircle },
  { name: 'Exports', href: '/exports', icon: FileText },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col w-64 bg-gray-900 border-r border-gray-800">
      <div className="flex items-center justify-center h-16 border-b border-gray-800">
        <h1 className="text-xl font-bold text-white">Sports Intel</h1>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-8">
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
          onClick={() => signOut({ callbackUrl: '/auth/signin' })}
          className="flex items-center w-full px-3 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut className="mr-3 h-5 w-5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
