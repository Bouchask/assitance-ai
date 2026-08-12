import React from "react";
import { cn } from "../../lib/utils";

export const Card = React.forwardRef(({ className, featured = false, children, ...props }, ref) => {
  if (featured) {
    return (
      <div className={cn("rounded-2xl bg-gradient-to-br from-accent via-accent-secondary to-accent p-[2px] shadow-accent-lg transition-all duration-300 hover:-translate-y-1", className)}>
        <div className="h-full w-full rounded-[calc(1.5rem-2px)] bg-card p-6 md:p-8" ref={ref} {...props}>
          {children}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={ref}
      className={cn(
        "rounded-2xl bg-card border border-border shadow-md transition-all duration-300 hover:shadow-xl hover:-translate-y-1 p-6 md:p-8",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});
Card.displayName = "Card";
