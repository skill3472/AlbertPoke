<script lang="ts">
  import { auth } from "../stores/auth.svelte";
  import { navigate, router } from "../router/router.svelte";

  const links: { path: string; label: string }[] = [
    { path: "/", label: "Poke" },
    { path: "/find-friends", label: "Find Friends" },
    { path: "/profile", label: "Profile" },
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
  <div class="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
    <a
      href="#/"
      class="text-primary font-mono text-lg font-black tracking-tighter uppercase"
    >
      Albert<span class="text-text">Poke</span>
    </a>

    <nav class="flex items-center gap-1 font-mono text-xs font-bold tracking-widest uppercase">
      {#each links as link (link.path)}
        <a
          href="#{link.path}"
          class="border-2 px-3 py-2 transition-colors {isActive(link.path)
            ? 'border-primary bg-primary text-primary-fg'
            : 'text-text-dim hover:border-border-strong border-transparent hover:bg-surface-hover'}"
        >
          {link.label}
        </a>
      {/each}
      <button
        type="button"
        onclick={logout}
        class="border-danger text-danger hover:bg-danger hover:text-primary-fg ml-2 cursor-pointer border-2 px-3 py-2 transition-colors"
      >
        Logout
      </button>
    </nav>
  </div>
</header>
