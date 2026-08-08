const pokeSound = new Audio("/poke.mp3");

export function playPokeSound(): void {
  pokeSound.currentTime = 0;
  pokeSound.play().catch((err) => console.error("[pokeSound] failed to play:", err));
}
