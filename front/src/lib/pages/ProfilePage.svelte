<script lang="ts">
  import { ApiError } from "../api/client";
  import { addFriend, checkMutualFriends, listFriends } from "../api/friends";
  import { getUser } from "../api/users";
  import type { FriendBrief, UserRead } from "../api/types";
  import Button from "../components/Button.svelte";
  import Card from "../components/Card.svelte";
  import { navigate } from "../router/router.svelte";
  import { auth } from "../stores/auth.svelte";
  import { notifications } from "../stores/notifications.svelte";
  import { toasts } from "../stores/toast.svelte";

  let { userId }: { userId?: number } = $props();

  const isOwnProfile = $derived(userId === undefined || userId === auth.user?.id);

  let viewedUser = $state<UserRead | null>(null);
  let myFriends = $state<FriendBrief[]>([]);
  let mutual = $state(false);
  let adding = $state(false);
  let loading = $state(true);

  $effect(() => {
    void load(userId);
  });

  async function load(targetId: number | undefined): Promise<void> {
    loading = true;
    try {
      myFriends = await listFriends();
      if (targetId !== undefined && targetId !== auth.user?.id && auth.user) {
        const [user, mutualResult] = await Promise.all([
          getUser(targetId),
          checkMutualFriends(auth.user.id, targetId),
        ]);
        viewedUser = user;
        mutual = mutualResult.mutual;
      } else {
        viewedUser = null;
      }
    } catch (err) {
      toasts.push(err instanceof ApiError ? err.message : "Failed to load profile.", "error");
    } finally {
      loading = false;
    }
  }

  const alreadyAdded = $derived(
    viewedUser !== null && myFriends.some((friend) => friend.id === viewedUser?.id),
  );

  async function add(): Promise<void> {
    if (!viewedUser) return;
    adding = true;
    try {
      const result = await addFriend(viewedUser.id);
      mutual = result.mutual;
      myFriends = [...myFriends, { id: viewedUser.id, name: viewedUser.name }];
      toasts.push(
        result.mutual
          ? `You and ${viewedUser.name} are now mutual friends!`
          : `Added ${viewedUser.name}.`,
        "success",
      );
    } catch (err) {
      toasts.push(err instanceof ApiError ? err.message : "Could not add friend.", "error");
    } finally {
      adding = false;
    }
  }

  async function toggleNotifications(): Promise<void> {
    if (notifications.enabled) {
      await notifications.disable();
      return;
    }
    await notifications.requestPermission();
    if (notifications.permission === "denied") {
      toasts.push("Notifications are blocked in your browser settings.", "error");
    } else if (!notifications.enabled) {
      toasts.push("Could not enable notifications. Please try again.", "error");
    }
  }
</script>

<div class="flex flex-col gap-8">
  {#if loading}
    <p class="text-text-muted animate-pulse font-mono text-sm uppercase">Loading...</p>
  {:else if !isOwnProfile && viewedUser}
    <div>
      <button
        type="button"
        onclick={() => navigate("/profile")}
        class="text-link mb-4 block font-mono text-xs uppercase underline"
      >
        &larr; Back to your profile
      </button>
      <h1 class="text-text font-mono text-2xl font-black tracking-tight uppercase">
        {viewedUser.name}
      </h1>
    </div>

    <Card>
      <p class="text-text-muted font-mono text-xs tracking-widest uppercase">User ID</p>
      <p class="text-text mt-1 font-mono">#{viewedUser.id}</p>
      <div class="mt-4">
        {#if mutual}
          <span class="border-accent text-accent border-2 px-3 py-1.5 font-mono text-xs uppercase">
            Mutual Friends
          </span>
        {:else if alreadyAdded}
          <span
            class="border-border-strong text-text-muted border-2 px-3 py-1.5 font-mono text-xs uppercase"
          >
            Added — waiting for them
          </span>
        {:else}
          <Button size="sm" variant="secondary" disabled={adding} onclick={add}>
            {adding ? "Adding..." : "Add Friend"}
          </Button>
        {/if}
      </div>
    </Card>
  {:else}
    <div>
      <h1 class="text-text font-mono text-2xl font-black tracking-tight uppercase">Profile</h1>
    </div>

    <Card>
      <p class="text-text-muted font-mono text-xs tracking-widest uppercase">Name</p>
      <p class="text-text mt-1 font-mono text-xl font-bold">{auth.user?.name}</p>
      <p class="text-text-muted mt-4 font-mono text-xs tracking-widest uppercase">User ID</p>
      <p class="text-text mt-1 font-mono">#{auth.user?.id}</p>
    </Card>

    <Card>
      <p class="text-text-muted font-mono text-xs tracking-widest uppercase">Browser Notifications</p>
      <p class="text-text-dim mt-1 font-mono text-sm">
        Get notified in your browser when a friend pokes you back.
      </p>
      <div class="mt-4">
        {#if !notifications.supported}
          <p class="text-text-muted font-mono text-xs uppercase">Not supported in this browser.</p>
        {:else if notifications.permission === "denied"}
          <p class="text-danger font-mono text-xs uppercase">Blocked — enable in browser settings.</p>
        {:else}
          <Button
            variant={notifications.enabled ? "secondary" : "primary"}
            size="sm"
            onclick={toggleNotifications}
          >
            {notifications.enabled ? "Disable" : "Enable"} Notifications
          </Button>
        {/if}
      </div>
    </Card>

    <div>
      <h2 class="text-text font-mono text-lg font-bold tracking-tight uppercase">
        Friends ({myFriends.length})
      </h2>
      {#if myFriends.length === 0}
        <Card class="mt-3">
          <p class="text-text font-mono">You haven't added any friends yet.</p>
          <a href="#/find-friends" class="text-link mt-2 inline-block font-mono text-sm underline">
            Find friends &rarr;
          </a>
        </Card>
      {:else}
        <div class="mt-3 flex flex-col gap-2">
          {#each myFriends as friend (friend.id)}
            <a href="#/profile/{friend.id}" class="block">
              <Card class="hover:bg-surface-hover p-4! transition-colors">
                <span class="text-text font-mono">{friend.name}</span>
              </Card>
            </a>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
