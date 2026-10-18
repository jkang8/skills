import { Slot } from "@radix-ui/react-slot";
import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "destructive"; asChild?: boolean };

const styles = {
  primary: "bg-primary text-primary-foreground",
  secondary: "border border-border bg-background text-foreground",
  ghost: "text-foreground hover:bg-border/40",
  destructive: "bg-danger text-primary-foreground",
};

export function Button({ variant = "primary", asChild, className = "", ...props }: Props) {
  const C = asChild ? Slot : "button";
  return <C className={`inline-flex h-8 items-center gap-2 rounded-md px-3 text-sm font-medium transition-[transform,opacity] duration-150 active:scale-[0.97] ${styles[variant]} ${className}`} {...props} />;
}
