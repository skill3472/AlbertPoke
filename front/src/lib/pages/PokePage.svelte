<script lang="ts">
  import { onMount } from "svelte";
  import { ApiError } from "../api/client";
  import { listFriends } from "../api/friends";
  import { checkPoke, listPokeThreads, sendPoke } from "../api/pokes";
  import Card from "../components/Card.svelte";
  import PokeButton from "../components/PokeButton.svelte";
  import PokeListRow from "../components/PokeListRow.svelte";
  import type { PokeButtonStatus } from "../components/pokeButtonStatus";
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
  }

  let entries = $state<PokeEntry[]>([]);
  let loading = $state(true);

  onMount(() => {
    void load();
  });

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
        });
      });

      entries = Array.from(byId.values()).sort((a, b) => a.name.localeCompare(b.name));
    } catch (err) {
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
      entry.pokeTrigger += 1;
    } catch (err) {
      toasts.push(err instanceof ApiError ? err.message : "Poke failed.", "error");
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
          pokeTrigger={entry.pokeTrigger}
          onpoke={() => poke(entry)}
        />
      {/each}
    </div>
  {/if}
</div>
