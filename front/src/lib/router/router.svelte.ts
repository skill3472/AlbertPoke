function currentPath(): string {
  return window.location.hash.slice(1) || "/";
}

class Router {
  path = $state(currentPath());

  constructor() {
    window.addEventListener("hashchange", () => {
      this.path = currentPath();
    });
  }
}

export const router = new Router();

export function navigate(path: string): void {
  window.location.hash = path;
}

export function parseProfileId(path: string): number | undefined {
  const match = /^\/profile\/(\d+)$/.exec(path);
  return match?.[1] !== undefined ? Number(match[1]) : undefined;
}
