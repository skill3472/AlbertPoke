<script lang="ts">
  interface Props {
    label: string;
    id: string;
    type?: "text" | "password";
    value?: string;
    placeholder?: string;
    error?: string;
    autocomplete?: AutoFill;
    oninput?: (event: Event) => void;
  }

  let {
    label,
    id,
    type = "text",
    value = $bindable(""),
    placeholder = "",
    error = "",
    autocomplete,
    oninput,
  }: Props = $props();
</script>

<div class="flex flex-col gap-1.5">
  <label for={id} class="text-text-muted font-mono text-xs tracking-widest uppercase">{label}</label>
  <input
    {id}
    {type}
    {placeholder}
    {autocomplete}
    {oninput}
    bind:value
    class="bg-surface text-text placeholder:text-text-muted border-2 px-3 py-2.5 focus:outline-none {error
      ? 'border-danger'
      : 'border-border focus:border-primary'}"
  />
  {#if error}
    <p class="text-danger font-mono text-xs">{error}</p>
  {/if}
</div>
