<script lang="ts">
  import { auth } from "../stores/auth.svelte";
  import { navigate, router } from "../router/router.svelte";
  import Icon from "./Icon.svelte";
  import type { IconName } from "./Icon.svelte";

  const links: { path: string; label: string; icon: IconName }[] = [
    { path: "/", label: "Poke", icon: "poke" },
    { path: "/find-friends", label: "Find Friends", icon: "friends" },
    { path: "/profile", label: "Profile", icon: "profile" },
  ];

  function isActive(path: string): boolean {
    return router.path === path;
  }

  function logout(): void {
    auth.logout();
    navigate("/login");
  }
</script>

<header class="border-border-strong bg-surface sticky top-0 z-40 border-b-2">
  <div class="mx-auto flex max-w-3xl items-center justify-between px-3 py-3 sm:px-4">
    <a
      href="#/"
      class="text-primary shrink-0 font-mono text-lg font-black tracking-tighter uppercase"
    >
      Albert<span class="text-text">Poke</span>
    </a>

    <nav class="flex items-center gap-1 font-mono text-xs font-bold tracking-widest uppercase">
      {#each links as link (link.path)}
        <a
          href="#{link.path}"
          aria-label={link.label}
          title={link.label}
          class="flex items-center gap-2 border-2 px-2.5 py-2 transition-colors sm:px-3 {isActive(
            link.path,
          )
            ? 'border-primary bg-primary text-primary-fg'
            : 'text-text-dim hover:border-border-strong border-transparent hover:bg-surface-hover'}"
        >
          <Icon name={link.icon} />
          <span class="hidden sm:inline">{link.label}</span>
        </a>
      {/each}
      <button
        type="button"
        onclick={logout}
        aria-label="Logout"
        title="Logout"
        class="border-danger text-danger hover:bg-danger hover:text-primary-fg ml-1 flex cursor-pointer items-center gap-2 border-2 px-2.5 py-2 transition-colors sm:ml-2 sm:px-3"
      >
        <Icon name="logout" />
        <span class="hidden sm:inline">Logout</span>
      </button>
    </nav>
  </div>
</header>
