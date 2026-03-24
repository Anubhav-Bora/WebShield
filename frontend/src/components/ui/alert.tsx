'use client';

import React from 'react';

interface AlertProps {
  children: React.ReactNode;
  className?: string;
}

export function Alert({ children, className }: AlertProps) {
  return (
    <div className={`p-4 rounded-lg border ${className || 'bg-blue-50 border-blue-200'}`}>
      {children}
    </div>
  );
}

export function AlertDescription({ children, className }: AlertProps) {
  return <p className={`text-sm ${className || ''}`}>{children}</p>;
}
