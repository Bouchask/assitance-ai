import React from "react";
import { cn } from "../../lib/utils";

export function Headline({ children, className, as: Component = "h1", ...props }) {
  return (
    <Component
      className={cn(
        "font-display text-4xl md:text-[3.25rem] lg:text-[5.25rem] font-normal tracking-tight leading-[1.1] text-foreground",
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export function Subhead({ children, className, as: Component = "h2", ...props }) {
  return (
    <Component
      className={cn(
        "font-display text-3xl md:text-[3.25rem] font-normal tracking-normal leading-[1.15] text-foreground",
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export function Body({ children, className, as: Component = "p", ...props }) {
  return (
    <Component
      className={cn(
        "font-sans text-base md:text-lg tracking-normal leading-relaxed text-muted-foreground",
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export function MonoLabel({ children, className, as: Component = "span", ...props }) {
  return (
    <Component
      className={cn(
        "font-mono text-xs uppercase tracking-[0.15em] text-accent",
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export function SectionBadge({ children, className }) {
  return (
    <div className={cn("inline-flex items-center gap-3 rounded-full border border-accent/30 bg-accent/5 px-5 py-2", className)}>
      <span className="h-2 w-2 rounded-full bg-accent animate-pulse" />
      <MonoLabel>{children}</MonoLabel>
    </div>
  );
}
