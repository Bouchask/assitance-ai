import React from "react";
import { cn } from "../../lib/utils";

export const Button = React.forwardRef(({ 
  className, 
  variant = "primary", 
  size = "default",
  children, 
  ...props 
}, ref) => {
  const baseStyles = "group relative inline-flex items-center justify-center whitespace-nowrap font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98] rounded-xl";
  
  const variants = {
    primary: "bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-secondary)] text-white shadow-sm hover:shadow-[var(--shadow-accent-lg)] hover:-translate-y-0.5 hover:brightness-110",
    secondary: "border border-border bg-transparent text-foreground hover:border-accent/30 hover:shadow-md hover:-translate-y-0.5",
    ghost: "text-muted-foreground hover:text-foreground hover:bg-muted"
  };

  const sizes = {
    default: "h-12 px-6 py-3 gap-2.5",
    sm: "h-10 px-4 py-2 gap-2 text-sm",
    lg: "h-14 px-8 py-4 gap-3 text-lg"
  };

  return (
    <button
      ref={ref}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
});
Button.displayName = "Button";
