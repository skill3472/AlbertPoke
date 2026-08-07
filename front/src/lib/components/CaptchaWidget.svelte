<script lang="ts">
  import "altcha";
  import { onMount } from "svelte";

  interface AltchaStateChangeDetail {
    payload?: string;
    state: "unverified" | "verifying" | "verified" | "error";
  }

  let { value = $bindable("") }: { value?: string } = $props();

  let container: HTMLDivElement | undefined;

  onMount(() => {
    const widget = container?.querySelector("altcha-widget");
    if (!widget) return;

    const onStateChange = (event: Event): void => {
      const detail = (event as CustomEvent<AltchaStateChangeDetail>).detail;
      value = detail.state === "verified" ? (detail.payload ?? "") : "";
    };

    widget.addEventListener("statechange", onStateChange);
    return () => widget.removeEventListener("statechange", onStateChange);
  });
</script>

<div bind:this={container} class="altcha-container">
  <altcha-widget challenge="/api/users/captcha" name="altcha" hidefooter></altcha-widget>
</div>

<style>
  .altcha-container {
    --altcha-color-base: var(--color-surface);
    --altcha-color-border: var(--color-border);
    --altcha-color-text: var(--color-text);
    --altcha-color-border-focus: var(--color-primary);
    --altcha-border-width: 2px;
    --altcha-radius-border: 0px;
    --altcha-radius-outer: 0px;
  }
</style>
