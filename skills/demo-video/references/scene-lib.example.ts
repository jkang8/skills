// Template: copy into your project (for example demo/lib/scene.ts) and adjust. One scene is one short clip with its
// own browser, so a broken scene is re-recorded alone. recordScene writes $SCENE_CLIPS/<name>.mp4 and <name>.json
// (duration and caption cues, in seconds from the clip's first frame): the contract scripts/stitch.py reads.
import { chromium } from "playwright"
import type { Locator, Page } from "playwright"
import { execFileSync } from "node:child_process"
import { mkdirSync, readdirSync, renameSync, rmSync, writeFileSync } from "node:fs"

export const W = 1440
export const H = 900
const clips = (process.env.SCENE_CLIPS ?? "clips").replace(/\/?$/, "/")
const ffmpeg = process.env.FFMPEG ?? "ffmpeg"
const raw = `${clips}raw/`

export type SceneContext = {
  page: Page
  base: string
  start: () => void // mark the first frame worth keeping, after the first screen has rendered
  say: (text: string) => Promise<void> // show a caption; the next say() waits for this one's reading time
  hold: () => Promise<void> // wait out the current caption before closing what it describes
  moveTo: (target: Locator) => Promise<void>
  click: (target: Locator, pauseAfter?: number) => Promise<void>
  pause: (ms: number) => Promise<void>
}
export type Scene = { name: string; run: (ctx: SceneContext) => Promise<void> }
export const defineScene = (s: Scene): Scene => s

// Keep in step with captions.reading_seconds in scripts/captions.py.
const readingMs = (text: string) => Math.max(2600, text.split(/\s+/).length * 285 + 800)

// Headless video draws no pointer, so draw one that follows real mouse events, plus a click ring.
const overlay = `addEventListener("DOMContentLoaded", () => {
  const c = document.createElement("div")
  c.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24"><path d="M5 3l14 8-6.5 1.5L9 19z" fill="#18181b" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>'
  Object.assign(c.style, { position: "fixed", left: "0", top: "0", zIndex: "2147483647", pointerEvents: "none", transform: "translate(-100px,-100px)" })
  const ring = document.createElement("div")
  Object.assign(ring.style, { position: "fixed", width: "28px", height: "28px", borderRadius: "999px", zIndex: "2147483646", pointerEvents: "none", border: "2px solid rgba(37,99,235,.55)", opacity: "0", transition: "opacity 200ms ease-out" })
  document.body.append(c, ring)
  addEventListener("mousemove", (e) => { c.style.transform = "translate(" + (e.clientX - 4) + "px," + (e.clientY - 3) + "px)" }, true)
  addEventListener("mousedown", (e) => { ring.style.left = e.clientX - 14 + "px"; ring.style.top = e.clientY - 14 + "px"; ring.style.opacity = "1"; setTimeout(() => (ring.style.opacity = "0"), 220) }, true)
})`

export async function recordScene(scene: Scene, base = process.env.BASE_URL ?? "http://localhost:3000") {
  const dir = `${raw}${scene.name}/`
  rmSync(dir, { recursive: true, force: true })
  mkdirSync(dir, { recursive: true })
  const browser = await chromium.launch()
  const context = await browser.newContext({ viewport: { width: W, height: H }, colorScheme: "light", recordVideo: { dir, size: { width: W, height: H } } })
  await context.addInitScript(overlay)
  await context.addInitScript(() => { try { localStorage.clear() } catch {} }) // every scene starts from clean state
  const t0 = Date.now()
  const page = await context.newPage()

  let pos = { x: W / 2, y: H / 2 }
  let clock0 = t0
  let holdUntil = 0
  const cues: { start: number; text: string }[] = []
  const hold = async () => { const wait = holdUntil - Date.now(); if (wait > 0) await page.waitForTimeout(wait) }
  const moveTo = async (target: Locator) => {
    await target.waitFor({ state: "visible" })
    await target.scrollIntoViewIfNeeded()
    const box = (await target.boundingBox())!
    const x = box.x + box.width / 2, y = box.y + box.height / 2
    await page.mouse.move(x, y, { steps: Math.min(18, Math.max(6, Math.round(Math.hypot(x - pos.x, y - pos.y) / 70))) })
    pos = { x, y }
  }
  await scene.run({
    page, base, hold, moveTo,
    start: () => { clock0 = Date.now() },
    say: async (text) => { await hold(); holdUntil = Date.now() + readingMs(text); cues.push({ start: (Date.now() - clock0) / 1000, text }) },
    click: async (target, pauseAfter = 500) => {
      await moveTo(target); await page.waitForTimeout(250)
      await page.mouse.down(); await page.waitForTimeout(70); await page.mouse.up(); await page.waitForTimeout(pauseAfter)
    },
    pause: (ms) => page.waitForTimeout(ms),
  })
  await hold() // the last caption stays until it can be read
  await page.waitForTimeout(300) // tail pad: a crossfade (up to 0.3s) dissolves the end of the clip and must not eat the caption
  const duration = (Date.now() - clock0) / 1000
  const trim = (clock0 - t0) / 1000
  const video = page.video()!
  await context.close()
  await browser.close()
  const kept = `${dir}scene.webm`
  renameSync(await video.path(), kept)
  for (const f of readdirSync(dir)) if (f !== "scene.webm") rmSync(`${dir}${f}`)
  mkdirSync(clips, { recursive: true })
  execFileSync(ffmpeg, ["-y", "-loglevel", "error", "-ss", trim.toFixed(2), "-i", kept, "-t", duration.toFixed(2),
    "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30", "-an", `${clips}${scene.name}.mp4`])
  writeFileSync(`${clips}${scene.name}.json`, JSON.stringify({ name: scene.name, duration, cues }, null, 2) + "\n")
}
