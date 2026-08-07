<script lang="ts">
  import type { Snippet } from "svelte";

  let { class: className = "", children }: { class?: string; children: Snippet } = $props();
</script>

<div class="border-border shadow-hard bg-surface border-2 p-6 {className}">
  {@render children()}
</div>
