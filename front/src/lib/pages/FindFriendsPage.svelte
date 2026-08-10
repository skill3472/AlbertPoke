<script lang="ts">
  import { ApiError } from "../api/client";
  import { addFriend } from "../api/friends";
  import { searchUsers } from "../api/users";
  import type { UserRead } from "../api/types";
  import Button from "../components/Button.svelte";
  import Card from "../components/Card.svelte";
  import TextField from "../components/TextField.svelte";
  import { auth } from "../stores/auth.svelte";
  import { toasts } from "../stores/toast.svelte";

  const DEBOUNCE_MS = 300;

  type AddState = "idle" | "adding" | "added" | "mutual";

  let query = $state("");
  let results = $state<UserRead[]>([]);
  let addStates = $state<Record<number, AddState>>({});
  let searching = $state(false);
  let searched = $state(false);
  let debounceHandle: ReturnType<typeof setTimeout> | undefined;

  function onQueryInput(): void {
    if (debounceHandle) clearTimeout(debounceHandle);
    debounceHandle = setTimeout(() => void search(), DEBOUNCE_MS);
  }

  async function search(): Promise<void> {
    const trimmed = query.trim();
    if (!trimmed) {
      results = [];
      searched = false;
      return;
    }
    searching = true;
    try {
      const found = await searchUsers(trimmed);
      results = found.filter((user) => user.id !== auth.user?.id);
      searched = true;
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return;
      toasts.push(err instanceof ApiError ? err.message : "Search failed.", "error");
    } finally {
      searching = false;
    }
  }

  async function add(user: UserRead): Promise<void> {
    addStates[user.id] = "adding";
    try {
      const result = await addFriend(user.id);
      addStates[user.id] = result.mutual ? "mutual" : "added";
      toasts.push(
        result.mutual ? `You and ${user.name} are now mutual friends!` : `Added ${user.name}.`,
        "success",
      );
    } catch (err) {
      addStates[user.id] = "idle";
      if (err instanceof ApiError && err.status === 401) return;
      toasts.push(err instanceof ApiError ? err.message : "Could not add friend.", "error");
    }
  }
</script>

<div class="flex flex-col gap-8">
  <div>
    <h1 class="text-text font-mono text-2xl font-black tracking-tight uppercase">Find Friends</h1>
    <p class="text-text-muted mt-1 font-mono text-sm">Search by name and add people to poke.</p>
  </div>

  <TextField
    id="friend-search"
    label="Search"
    placeholder="Enter a name..."
    bind:value={query}
    oninput={onQueryInput}
  />

  {#if searching}
    <p class="text-text-muted animate-pulse font-mono text-sm uppercase">Searching...</p>
  {:else if searched && results.length === 0}
    <p class="text-text-muted font-mono text-sm">No users found.</p>
  {:else}
    <div class="flex flex-col gap-3">
      {#each results as user (user.id)}
        <Card class="flex items-center justify-between p-4!">
          <span class="text-text font-mono">{user.name}</span>
          {#if addStates[user.id] === "added"}
            <span class="border-success text-success border-2 px-3 py-1.5 font-mono text-xs uppercase"
              >Added</span
            >
          {:else if addStates[user.id] === "mutual"}
            <span class="border-accent text-accent border-2 px-3 py-1.5 font-mono text-xs uppercase"
              >Mutual</span
            >
          {:else}
            <Button
              size="sm"
              variant="secondary"
              disabled={addStates[user.id] === "adding"}
              onclick={() => add(user)}
            >
              {addStates[user.id] === "adding" ? "Adding..." : "Add Friend"}
            </Button>
          {/if}
        </Card>
      {/each}
    </div>
  {/if}
</div>
