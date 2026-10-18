import type { InputHTMLAttributes } from "react";

export function Input({ className = "", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`h-8 w-full rounded-md border border-border bg-background px-2 text-sm ${className}`} {...props} />;
}
