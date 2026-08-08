<script lang="ts">
  import { onMount } from "svelte";
  import Navbar from "./lib/components/Navbar.svelte";
  import ToastContainer from "./lib/components/ToastContainer.svelte";
  import FindFriendsPage from "./lib/pages/FindFriendsPage.svelte";
  import LoginPage from "./lib/pages/LoginPage.svelte";
  import PokePage from "./lib/pages/PokePage.svelte";
  import ProfilePage from "./lib/pages/ProfilePage.svelte";
  import RegisterPage from "./lib/pages/RegisterPage.svelte";
  import { router, navigate, parseProfileId } from "./lib/router/router.svelte";
  import { auth } from "./lib/stores/auth.svelte";
  import { notifications } from "./lib/stores/notifications.svelte";

  const PUBLIC_PATHS = new Set(["/login", "/register"]);

  const profileId = $derived(parseProfileId(router.path));
  const isProfileRoute = $derived(router.path === "/profile" || profileId !== undefined);

  onMount(() => {
    void auth.init();
  });

  $effect(() => {
    if (!auth.ready) return;
    const isPublic = PUBLIC_PATHS.has(router.path);
    if (!auth.isAuthenticated && !isPublic) {
      navigate("/login");
    } else if (auth.isAuthenticated && isPublic) {
      navigate("/");
    }
  });

  $effect(() => {
    if (auth.isAuthenticated) {
      void notifications.ensureSubscribed();
    }
  });
</script>

<ToastContainer />

{#if !auth.ready}
  <div class="bg-bg flex min-h-screen items-center justify-center">
    <p class="text-text-muted animate-pulse font-mono text-sm uppercase">Loading...</p>
  </div>
{:else if router.path === "/login"}
  <LoginPage />
{:else if router.path === "/register"}
  <RegisterPage />
{:else if auth.isAuthenticated}
  <div class="bg-bg min-h-screen">
    <Navbar />
    <main class="mx-auto max-w-3xl px-4 py-8">
      {#if router.path === "/"}
        <PokePage />
      {:else if router.path === "/find-friends"}
        <FindFriendsPage />
      {:else if isProfileRoute}
        <ProfilePage userId={profileId} />
      {:else}
        <p class="text-text-muted font-mono">Page not found.</p>
      {/if}
    </main>
  </div>
{/if}
