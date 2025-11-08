import React, { useState } from 'react';
import { FactCheckNote } from '@/types';
import { CheckCircle, ExternalLink, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';

interface Props {
  note: FactCheckNote;
  children: React.ReactNode;
}

function FactCheckTooltip({ note, children }: Props) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative inline-block">
      <span
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className="cursor-help border-b border-dotted border-accent"
      >
        {children}
      </span>

      {isOpen && (
        <div className="absolute z-50 w-80 p-4 bg-sidebar-bg border border-gray-700 rounded-lg shadow-xl bottom-full left-0 mb-2">
          <div className="flex items-start gap-2 mb-3">
            {note.verified ? (
              <CheckCircle size={18} className="text-green-500 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle size={18} className="text-yellow-500 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-200 mb-1">
                {note.verified ? 'Verified Fact' : 'Unverified Data'}
              </p>
              <p className="text-xs text-gray-400">{note.text}</p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">Source:</span>
              <a
                href={note.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:underline flex items-center gap-1"
              >
                {note.source}
                <ExternalLink size={12} />
              </a>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">Last checked:</span>
              <span className="text-gray-400">
                {format(note.timestamp, 'MMM d, h:mm a')}
              </span>
            </div>
          </div>

          {/* Arrow */}
          <div className="absolute top-full left-4 -mt-px">
            <div className="border-8 border-transparent border-t-sidebar-bg" />
          </div>
        </div>
      )}
    </div>
  );
}

export default FactCheckTooltip;
