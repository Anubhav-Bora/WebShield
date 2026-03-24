'use client';

import React from 'react';

interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export function Tabs({ value, onValueChange, children, className }: TabsProps) {
  return (
    <div className={className}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as any, { value, onValueChange });
        }
        return child;
      })}
    </div>
  );
}

interface TabsListProps {
  children: React.ReactNode;
  className?: string;
}

export function TabsList({ children, className }: TabsListProps) {
  return (
    <div className={`flex gap-1 border-b border-gray-200 ${className || ''}`}>
      {children}
    </div>
  );
}

interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  onValueChange?: (value: string) => void;
  className?: string;
}

export function TabsTrigger({ value, children, onValueChange, className }: TabsTriggerProps) {
  const [activeValue, setActiveValue] = React.useState<string>();
  const isActive = value === (onValueChange ? activeValue : value);

  return (
    <button
      onClick={() => {
        setActiveValue(value);
        onValueChange?.(value);
      }}
      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
        isActive
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      } ${className || ''}`}
    >
      {children}
    </button>
  );
}

interface TabsContentProps {
  value: string;
  children: React.ReactNode;
  activeValue?: string;
  className?: string;
}

export function TabsContent({ value, children, activeValue, className }: TabsContentProps) {
  if (value !== activeValue) return null;
  return <div className={className}>{children}</div>;
}
