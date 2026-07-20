// Motion central — anime.js v3. Toda config de duração/easing fica aqui.
// Tudo respeita prefers-reduced-motion (duração 0, sem loop).
import anime from 'animejs/lib/anime.es.js'

export const REDUCE =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const d = (ms) => (REDUCE ? 0 : ms)

// Barras de score "assentam" como instrumento; número conta junto.
export function animateScoreBars(root = document) {
  const fills = root.querySelectorAll('.score-fill')
  anime({
    targets: fills,
    width: (el) => `${el.dataset.score}%`,
    duration: d(520),
    easing: 'easeOutCubic',
    delay: anime.stagger(18),
  })
}

// Count-up de um número (tiles de métrica).
export function countUp(el, to, dur = 700) {
  if (!el) return
  if (REDUCE) { el.textContent = String(to); return }
  const obj = { v: 0 }
  anime({
    targets: obj,
    v: to,
    round: 1,
    duration: dur,
    easing: 'easeOutExpo',
    update: () => { el.textContent = String(obj.v) },
  })
}

// Farol pulsante (único loop do app).
export function beacon(el) {
  if (!el || REDUCE) return null
  return anime({
    targets: el,
    scale: [1, 1.15],
    opacity: [0.7, 1],
    duration: 2200,
    easing: 'easeInOutSine',
    direction: 'alternate',
    loop: true,
  })
}

export function drawerIn(el) {
  anime({ targets: el, translateX: [24, 0], opacity: [0, 1], duration: d(220), easing: 'easeOutQuart' })
}

export function selectionIn(el) {
  anime({ targets: el, translateY: [16, 0], opacity: [0, 1], duration: d(260), easing: 'easeOutCubic' })
}

export function fadeInUp(el, delay = 0) {
  anime({ targets: el, translateY: [12, 0], opacity: [0, 1], duration: d(420), easing: 'easeOutQuad', delay })
}

export function staggerRows(nodes) {
  anime({ targets: nodes, opacity: [0, 1], translateY: [8, 0], duration: d(240), easing: 'easeOutQuad', delay: anime.stagger(8) })
}

export function toastIn(el) {
  anime({ targets: el, translateX: [16, 0], opacity: [0, 1], duration: d(220), easing: 'easeOutQuad' })
}
