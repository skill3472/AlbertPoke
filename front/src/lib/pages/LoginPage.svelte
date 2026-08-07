<script lang="ts">
  import { ApiError } from "../api/client";
  import { login } from "../api/users";
  import Button from "../components/Button.svelte";
  import CaptchaWidget from "../components/CaptchaWidget.svelte";
  import Card from "../components/Card.svelte";
  import TextField from "../components/TextField.svelte";
  import { navigate } from "../router/router.svelte";
  import { auth } from "../stores/auth.svelte";
  import { toasts } from "../stores/toast.svelte";

  let name = $state("");
  let password = $state("");
  let captcha = $state("");
  let error = $state("");
  let submitting = $state(false);

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    if (!captcha) {
      error = "Please complete the captcha challenge.";
      return;
    }
    error = "";
    submitting = true;
    try {
      const token = await login(name, password, captcha);
      await auth.loginWithToken(token.access_token);
      toasts.push(`Welcome back, ${name}!`, "success");
      navigate("/");
    } catch (err) {
      error = err instanceof ApiError ? err.message : "Login failed.";
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
        <TextField id="login-name" label="Name" bind:value={name} autocomplete="username" />
        <TextField
          id="login-password"
          label="Password"
          type="password"
          bind:value={password}
          autocomplete="current-password"
        />
        <CaptchaWidget bind:value={captcha} />
        {#if error}
          <p class="text-danger font-mono text-xs">{error}</p>
        {/if}
        <Button type="submit" disabled={submitting}>
          {submitting ? "Logging in..." : "Log In"}
        </Button>
      </form>
      <p class="text-text-muted mt-6 text-center font-mono text-xs">
        No account? <a href="#/register" class="text-link underline">Register</a>
      </p>
    </Card>
  </div>
</div>
