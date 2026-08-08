import { getSettings, updateSettings } from "../api/settings";
import type { PokeLayout } from "../api/types";

const DEFAULT_POKE_LAYOUT: PokeLayout = "list";

class SettingsStore {
  pokeLayout = $state<PokeLayout>(DEFAULT_POKE_LAYOUT);
  loaded = $state(false);

  async load(): Promise<void> {
    try {
      const settings = await getSettings();
      this.pokeLayout = settings.poke_layout;
    } catch {
      this.pokeLayout = DEFAULT_POKE_LAYOUT;
    } finally {
      this.loaded = true;
    }
  }

  async setPokeLayout(layout: PokeLayout): Promise<void> {
    const previous = this.pokeLayout;
    this.pokeLayout = layout;
    try {
      await updateSettings({ poke_layout: layout });
    } catch {
      this.pokeLayout = previous;
      throw new Error("Could not save poke screen layout.");
    }
  }
}

export const settings = new SettingsStore();
