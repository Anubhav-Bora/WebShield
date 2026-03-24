'use client';

import React from 'react';
import { ChevronDown } from 'lucide-react';

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
}

export function Select({ value, onValueChange, children }: SelectProps) {
  return (
    <div>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as any, { value, onValueChange });
        }
        return child;
      })}
    </div>
  );
}

export function SelectTrigger({ value, placeholder, className }: any) {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={`w-full px-3 py-2 border border-gray-300 rounded-lg text-left text-sm flex items-center justify-between bg-white hover:bg-gray-50 ${className || ''}`}
      >
        <span>{value || placeholder}</span>
        <ChevronDown className="h-4 w-4 text-gray-600" />
      </button>
    </div>
  );
}

export function SelectValue({ placeholder }: any) {
  return <span>{placeholder}</span>;
}

interface SelectContentProps {
  children: React.ReactNode;
}

export function SelectContent({ children }: SelectContentProps) {
  return (
    <div className="border border-gray-300 rounded-lg mt-1 bg-white shadow-lg">
      {children}
    </div>
  );
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
  onValueChange?: (value: string) => void;
}

export function SelectItem({ value, children, onValueChange }: SelectItemProps) {
  return (
    <button
      onClick={() => onValueChange?.(value)}
      className="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm text-gray-900"
    >
      {children}
    </button>
  );
}
