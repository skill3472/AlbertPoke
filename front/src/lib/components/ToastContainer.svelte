<script lang="ts">
  import { toasts, type ToastKind } from "../stores/toast.svelte";

  const kindClass: Record<ToastKind, string> = {
    success: "border-success text-success",
    error: "border-danger text-danger",
    info: "border-accent text-accent",
  };
</script>

<div class="fixed right-4 bottom-4 z-50 flex w-72 flex-col gap-2">
  {#each toasts.items as toast (toast.id)}
    <div
      class="bg-surface shadow-hard-sm animate-toast-in border-2 px-4 py-3 font-mono text-sm {kindClass[
        toast.kind
      ]}"
      role="status"
    >
      {toast.message}
    </div>
  {/each}
</div>

<style>
  @keyframes toast-in {
    0% {
      transform: translateX(16px);
      opacity: 0;
    }
    100% {
      transform: translateX(0);
      opacity: 1;
    }
  }
  .animate-toast-in {
    animation: toast-in 0.2s ease-out;
  }
</style>
