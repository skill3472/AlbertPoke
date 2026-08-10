<script lang="ts">
  import { onMount } from "svelte";
  import { ApiError } from "../api/client";
  import { listFriends } from "../api/friends";
  import { checkPoke, listPokeThreads, sendPoke } from "../api/pokes";
  import type { PokeEvent } from "../api/types";
  import Card from "../components/Card.svelte";
  import PokeButton from "../components/PokeButton.svelte";
  import PokeListRow from "../components/PokeListRow.svelte";
  import type { PokeButtonStatus } from "../components/pokeButtonStatus";
  import { playPokeSound } from "../pokeSound";
  import { pokeSocket } from "../stores/pokeSocket.svelte";
  import { settings } from "../stores/settings.svelte";
  import { toasts } from "../stores/toast.svelte";

  interface PokeEntry {
    id: number;
    name: string;
    streak: number;
    canPoke: boolean;
    lastPokeMine: boolean;
    mutual: boolean;
    pending: boolean;
    pokeTrigger: number;
    /** Epoch ms when our own rate limit against them elapses; null if not cooling down. */
    cooldownUntil: number | null;
  }

  let entries = $state<PokeEntry[]>([]);
  let loading = $state(true);
  let now = $state(Date.now());

  onMount(() => {
    void load();
    const unsubscribe = pokeSocket.onPoke(handlePokeEvent);
    return () => {
      unsubscribe();
      stopTicking();
    };
  });

  // Ticks `now` once a second, only while some entry is actively cooling down,
  // and flips those entries back to "ready" itself once their countdown elapses -
  // that transition has no server event to tell us about it.
  let tickHandle: ReturnType<typeof setInterval> | null = null;

  $effect(() => {
    const hasCooldown = entries.some((e) => e.cooldownUntil !== null);
    if (hasCooldown) {
      startTicking();
    } else {
      stopTicking();
    }
  });

  function startTicking(): void {
    if (tickHandle !== null) return;
    tickHandle = setInterval(() => {
      now = Date.now();
      for (const entry of entries) {
        if (entry.cooldownUntil !== null && entry.cooldownUntil <= now) {
          entry.canPoke = true;
          entry.cooldownUntil = null;
        }
      }
    }, 1000);
  }

  function stopTicking(): void {
    if (tickHandle === null) return;
    clearInterval(tickHandle);
    tickHandle = null;
  }

  function cooldownUntilFrom(cooldownSeconds: number): number | null {
    return cooldownSeconds > 0 ? Date.now() + cooldownSeconds * 1000 : null;
  }

  function cooldownSecondsFor(entry: PokeEntry): number {
    if (entry.cooldownUntil === null) return 0;
    return Math.max(0, Math.ceil((entry.cooldownUntil - now) / 1000));
  }

  /**
   * A friend poked us in real time. If we already know about them, update their
   * entry in place (no refetch, so the burst animation/sound plays); a poke from
   * someone with no existing entry means a brand-new thread, so just reload.
   */
  function handlePokeEvent(event: PokeEvent): void {
    const entry = entries.find((e) => e.id === event.from_user_id);
    if (!entry) {
      void load();
      return;
    }
    entry.streak = event.streak;
    entry.canPoke = event.can_poke;
    entry.lastPokeMine = false;
    entry.cooldownUntil = cooldownUntilFrom(event.cooldown_seconds);
    entry.pokeTrigger += 1;
    playPokeSound();
    toasts.push(`${event.from_user_name} poked you!`, "info");
  }

  async function load(): Promise<void> {
    loading = true;
    try {
      const [threads, friends] = await Promise.all([listPokeThreads(), listFriends()]);
      const byId = new Map<number, PokeEntry>();
      for (const thread of threads) {
        byId.set(thread.user.id, {
          id: thread.user.id,
          name: thread.user.name,
          streak: thread.streak,
          canPoke: thread.can_poke,
          lastPokeMine: thread.last_poke_mine,
          mutual: thread.mutual,
          pending: false,
          pokeTrigger: 0,
          cooldownUntil: cooldownUntilFrom(thread.cooldown_seconds),
        });
      }

      const newFriends = friends.filter((friend) => !byId.has(friend.id));
      const statuses = await Promise.all(newFriends.map((friend) => checkPoke(friend.id)));
      newFriends.forEach((friend, i) => {
        const status = statuses[i];
        if (!status) return;
        byId.set(friend.id, {
          id: friend.id,
          name: friend.name,
          streak: status.streak,
          canPoke: status.can_poke,
          lastPokeMine: false,
          mutual: status.mutual,
          pending: false,
          pokeTrigger: 0,
          cooldownUntil: cooldownUntilFrom(status.cooldown_seconds),
        });
      });

      entries = Array.from(byId.values()).sort((a, b) => a.name.localeCompare(b.name));
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return;
      toasts.push(err instanceof ApiError ? err.message : "Failed to load pokes.", "error");
    } finally {
      loading = false;
    }
  }

  function statusFor(entry: PokeEntry): PokeButtonStatus {
    if (entry.pending) return "pending";
    if (!entry.mutual) return "locked";
    if (entry.canPoke) return "ready";
    return entry.lastPokeMine ? "poked" : "cooldown";
  }

  async function poke(entry: PokeEntry): Promise<void> {
    if (statusFor(entry) !== "ready") return;
    entry.pending = true;
    try {
      const result = await sendPoke(entry.id);
      entry.streak = result.current_streak;
      entry.canPoke = false;
      entry.lastPokeMine = true;
      entry.cooldownUntil = null;
      entry.pokeTrigger += 1;
    } catch (err) {
      if (!(err instanceof ApiError && err.status === 401)) {
        toasts.push(err instanceof ApiError ? err.message : "Poke failed.", "error");
      }
    } finally {
      entry.pending = false;
    }
  }
</script>

<div class="flex flex-col gap-8">
  <div>
    <h1 class="text-text font-mono text-2xl font-black tracking-tight uppercase">Poke</h1>
    <p class="text-text-muted mt-1 font-mono text-sm">
      Poke a friend, then wait for them to poke back.
    </p>
  </div>

  {#if loading}
    <p class="text-text-muted animate-pulse font-mono text-sm uppercase">Loading...</p>
  {:else if entries.length === 0}
    <Card>
      <p class="text-text font-mono">You don't have anyone to poke yet.</p>
      <a href="#/find-friends" class="text-link mt-2 inline-block font-mono text-sm underline">
        Find friends to poke &rarr;
      </a>
    </Card>
  {:else if settings.pokeLayout === "tiles"}
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      {#each entries as entry (entry.id)}
        <Card class="flex items-center justify-center">
          <PokeButton
            name={entry.name}
            streak={entry.streak}
            status={statusFor(entry)}
            cooldownSeconds={cooldownSecondsFor(entry)}
            pokeTrigger={entry.pokeTrigger}
            onpoke={() => poke(entry)}
          />
        </Card>
      {/each}
    </div>
  {:else}
    <div class="flex flex-col gap-3">
      {#each entries as entry (entry.id)}
        <PokeListRow
          name={entry.name}
          streak={entry.streak}
          status={statusFor(entry)}
          cooldownSeconds={cooldownSecondsFor(entry)}
          pokeTrigger={entry.pokeTrigger}
          onpoke={() => poke(entry)}
        />
      {/each}
    </div>
  {/if}
</div>
