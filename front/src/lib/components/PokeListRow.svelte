<script lang="ts">
  import type { PokeButtonStatus } from "./pokeButtonStatus";
  import Button from "./Button.svelte";

  interface Props {
    name: string;
    streak: number;
    status: PokeButtonStatus;
    /** Bump this number whenever a poke succeeds to replay the celebration. */
    pokeTrigger: number;
    onpoke: () => void;
  }

  let { name, streak, status, pokeTrigger, onpoke }: Props = $props();

  let flashing = $state(false);
  let firstRun = true;

  $effect(() => {
    void pokeTrigger;
    if (firstRun) {
      firstRun = false;
      return;
    }
    flashing = true;
    const timeout = setTimeout(() => {
      flashing = false;
    }, 500);
    return () => clearTimeout(timeout);
  });

  const emoji = $derived(streak > 100 ? "💯" : streak > 10 ? "🔥" : "");

  const label: Record<PokeButtonStatus, string> = {
    ready: "Poke",
    poked: "Poked",
    cooldown: "Wait",
    locked: "Not Mutual",
    pending: "...",
  };
</script>

<div
  class="border-border shadow-hard bg-surface flex items-center justify-between gap-4 border-2 p-4 transition-colors duration-200 {flashing
    ? 'bg-primary/15'
    : ''}"
>
  <div class="flex min-w-0 items-center gap-3">
    <span class="text-text truncate font-mono font-bold uppercase">{name}</span>
    <span class="text-text-muted flex shrink-0 items-center gap-1 font-mono text-sm">
      {streak}
      {#if emoji}
        <span class="animate-poke-emoji inline-block">{emoji}</span>
      {/if}
    </span>
  </div>
  <Button
    size="sm"
    variant={status === "ready" ? "primary" : "secondary"}
    disabled={status !== "ready"}
    onclick={onpoke}
  >
    {label[status]}
  </Button>
</div>

<style>
  @keyframes poke-emoji-pop {
    0% {
      transform: scale(0.4) rotate(-10deg);
      opacity: 0;
    }
    60% {
      transform: scale(1.3) rotate(6deg);
      opacity: 1;
    }
    100% {
      transform: scale(1) rotate(0deg);
      opacity: 1;
    }
  }
  .animate-poke-emoji {
    animation: poke-emoji-pop 0.5s ease-out;
  }
</style>
