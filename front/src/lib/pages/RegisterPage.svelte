<script lang="ts">
  import { ApiError } from "../api/client";
  import { registerUser } from "../api/users";
  import Button from "../components/Button.svelte";
  import CaptchaWidget from "../components/CaptchaWidget.svelte";
  import Card from "../components/Card.svelte";
  import TextField from "../components/TextField.svelte";
  import { navigate } from "../router/router.svelte";
  import { toasts } from "../stores/toast.svelte";

  let name = $state("");
  let password = $state("");
  let confirmPassword = $state("");
  let captcha = $state("");
  let error = $state("");
  let submitting = $state(false);

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (password !== confirmPassword) {
      error = "Passwords do not match.";
      return;
    }
    if (!captcha) {
      error = "Please complete the captcha challenge.";
      return;
    }
    error = "";
    submitting = true;
    try {
      await registerUser(name, password, captcha);
      toasts.push("Account created — log in to continue.", "success");
      navigate("/login");
    } catch (err) {
      error = err instanceof ApiError ? err.message : "Registration failed.";
    } finally {
      submitting = false;
    }
  }
</script>

<div class="bg-bg flex min-h-screen items-center justify-center px-4">
  <div class="w-full max-w-sm">
    <h1 class="text-text mb-8 text-center font-mono text-3xl font-black tracking-tighter uppercase">
      Albert<span class="text-primary">Poke</span>
    </h1>
    <Card>
      <form class="flex flex-col gap-5" onsubmit={submit}>
        <TextField id="register-name" label="Name" bind:value={name} autocomplete="username" />
        <TextField
          id="register-password"
          label="Password"
          type="password"
          bind:value={password}
          autocomplete="new-password"
        />
        <TextField
          id="register-confirm-password"
          label="Confirm Password"
          type="password"
          bind:value={confirmPassword}
          autocomplete="new-password"
        />
        <CaptchaWidget bind:value={captcha} />
        {#if error}
          <p class="text-danger font-mono text-xs">{error}</p>
        {/if}
        <Button type="submit" disabled={submitting}>
          {submitting ? "Creating account..." : "Register"}
        </Button>
      </form>
      <p class="text-text-muted mt-6 text-center font-mono text-xs">
        Already have an account? <a href="#/login" class="text-link underline">Log in</a>
      </p>
    </Card>
  </div>
</div>
