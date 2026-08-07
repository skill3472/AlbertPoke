<script lang="ts">
  import type { PokeButtonStatus } from "./pokeButtonStatus";

  interface Props {
    name: string;
    streak: number;
    status: PokeButtonStatus;
    /** Bump this number whenever a poke succeeds to replay the celebration. */
    pokeTrigger: number;
    onpoke: () => void;
  }

  let { name, streak, status, pokeTrigger, onpoke }: Props = $props();

  const PARTICLE_COUNT = 10;

  let bursting = $state(false);
  let particles = $state<{ id: number; angle: number }[]>([]);
  let particleSeq = 0;
  let firstRun = true;

  $effect(() => {
    void pokeTrigger;
    if (firstRun) {
      firstRun = false;
      return;
    }
    burst();
  });

  function burst(): void {
    bursting = true;
    particles = Array.from({ length: PARTICLE_COUNT }, (_, i) => ({
      id: particleSeq++,
      angle: (360 / PARTICLE_COUNT) * i,
    }));
    setTimeout(() => {
      bursting = false;
      particles = [];
    }, 650);
  }

  const emoji = $derived(streak > 100 ? "💯" : streak > 10 ? "🔥" : "");

  const label: Record<PokeButtonStatus, string> = {
    ready: "Poke",
    poked: "Poked",
    cooldown: "Wait",
    locked: "Not Mutual",
    pending: "...",
  };
</script>

<div class="flex flex-col items-center gap-4">
  <p class="text-text max-w-40 truncate font-mono text-lg font-bold tracking-wide uppercase">
    {name}
  </p>

  <div class="relative">
    {#each particles as particle (particle.id)}
      <span
        class="bg-primary pointer-events-none absolute top-1/2 left-1/2 h-3 w-3"
        style:--angle="{particle.angle}deg"
        style:animation="poke-spark 0.6s ease-out forwards"
      ></span>
    {/each}

    <button
      type="button"
      class="relative h-40 w-40 border-4 font-mono text-xl font-black tracking-widest uppercase transition-transform duration-75 active:translate-x-1 active:translate-y-1 active:shadow-none disabled:cursor-not-allowed disabled:border-border disabled:bg-surface-raised disabled:text-text-muted disabled:shadow-none {status ===
      'ready'
        ? 'border-border-strong bg-primary text-primary-fg shadow-hard'
        : ''} {bursting ? 'animate-poke-pulse' : ''}"
      disabled={status !== "ready"}
      onclick={onpoke}
    >
      {label[status]}
    </button>

    {#if bursting}
      <div class="bg-primary animate-poke-flash pointer-events-none absolute inset-0"></div>
    {/if}
  </div>

  <div class="flex items-center gap-2 font-mono">
    <span class="text-text text-3xl font-black">{streak}</span>
    {#if emoji}
      <span class="animate-poke-emoji text-3xl">{emoji}</span>
    {/if}
  </div>
  <p class="text-text-muted text-xs tracking-widest uppercase">Streak</p>
</div>

<style>
  @keyframes poke-pulse {
    0% {
      transform: scale(1);
    }
    35% {
      transform: scale(0.9);
    }
    65% {
      transform: scale(1.1);
    }
    100% {
      transform: scale(1);
    }
  }
  .animate-poke-pulse {
    animation: poke-pulse 0.4s ease-out;
  }

  @keyframes poke-flash {
    0% {
      opacity: 0.55;
    }
    100% {
      opacity: 0;
    }
  }
  .animate-poke-flash {
    animation: poke-flash 0.5s ease-out forwards;
  }

  @keyframes poke-spark {
    0% {
      opacity: 1;
      transform: translate(-50%, -50%) rotate(var(--angle)) translateY(0) scale(1);
    }
    100% {
      opacity: 0;
      transform: translate(-50%, -50%) rotate(var(--angle)) translateY(-70px) scale(0.4);
    }
  }

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
    display: inline-block;
    animation: poke-emoji-pop 0.5s ease-out;
  }
</style>
