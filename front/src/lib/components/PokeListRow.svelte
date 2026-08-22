<script lang="ts">
  import { playPokeSound } from "../pokeSound";
  import type { PokeButtonStatus } from "./pokeButtonStatus";
  import Button from "./Button.svelte";

  interface Props {
    name: string;
    streak: number;
    status: PokeButtonStatus;
    /** Seconds left on our own rate limit; only meaningful while status is "cooldown". */
    cooldownSeconds?: number;
    /** Bump this number whenever a poke succeeds to replay the celebration. */
    pokeTrigger: number;
    /** Bump this number when they poke us to replay the "you got poked" name animation. */
    pokedTrigger: number;
    onpoke: () => void;
  }

  let {
    name,
    streak,
    status,
    cooldownSeconds = 0,
    pokeTrigger,
    pokedTrigger,
    onpoke,
  }: Props = $props();

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

  let namePoked = $state(false);
  let namePokedFirstRun = true;

  $effect(() => {
    void pokedTrigger;
    if (namePokedFirstRun) {
      namePokedFirstRun = false;
      return;
    }
    namePoked = true;
    const timeout = setTimeout(() => {
      namePoked = false;
    }, 700);
    return () => clearTimeout(timeout);
  });

  const emoji = $derived(streak > 100 ? "💯" : streak > 10 ? "🔥" : "");

  const staticLabel: Record<Exclude<PokeButtonStatus, "cooldown">, string> = {
    ready: "Poke",
    poked: "Poked",
    locked: "Not Mutual",
    pending: "...",
  };
  const label = $derived(
    status === "cooldown" ? `Wait (${cooldownSeconds}s)` : staticLabel[status],
  );
</script>

<div
  class="border-border shadow-hard bg-surface flex items-center justify-between gap-4 border-2 p-4 transition-colors duration-200 {flashing
    ? 'bg-primary/15'
    : ''}"
>
  <div class="flex min-w-0 items-center gap-3">
    <span
      class="text-text truncate font-mono font-bold uppercase {namePoked
        ? 'animate-poked-name'
        : ''}">{name}</span
    >
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
    onclick={() => {
      playPokeSound();
      onpoke();
    }}
  >
    {label}
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

  @keyframes poked-name {
    0% {
      transform: scale(1) rotate(0deg);
    }
    30% {
      transform: scale(1.4) rotate(-10deg);
    }
    60% {
      transform: scale(1.15) rotate(6deg);
    }
    100% {
      transform: scale(1) rotate(0deg);
    }
  }
  .animate-poked-name {
    display: inline-block;
    animation: poked-name 0.7s ease-out;
  }
</style>
