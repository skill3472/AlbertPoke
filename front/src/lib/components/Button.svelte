<script lang="ts">
  import type { Snippet } from "svelte";

  interface Props {
    variant?: "primary" | "secondary" | "danger" | "ghost";
    size?: "sm" | "md" | "lg";
    type?: "button" | "submit";
    disabled?: boolean;
    onclick?: (event: MouseEvent) => void;
    children: Snippet;
  }

  let {
    variant = "primary",
    size = "md",
    type = "button",
    disabled = false,
    onclick,
    children,
  }: Props = $props();

  const variantClass: Record<NonNullable<Props["variant"]>, string> = {
    primary: "border-primary bg-primary text-primary-fg hover:bg-primary-hover",
    secondary: "border-border-strong bg-surface-raised text-text hover:bg-surface-hover",
    danger: "border-danger bg-danger text-primary-fg hover:bg-danger-hover",
    ghost: "border-transparent bg-transparent text-text hover:bg-surface-hover",
  };

  const sizeClass: Record<NonNullable<Props["size"]>, string> = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-5 py-2.5 text-sm",
    lg: "px-7 py-3.5 text-base",
  };
</script>

<button
  {type}
  {disabled}
  {onclick}
  class="cursor-pointer border-2 font-mono font-bold tracking-wide uppercase transition-colors duration-100 active:translate-x-0.5 active:translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40 {variantClass[
    variant
  ]} {sizeClass[size]}"
>
  {@render children()}
</button>
