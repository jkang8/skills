// One scene for a to-do app: it opens its own URL, builds its own state, and says one thing at a time.
// Run it alone (`node scenes/01-tasks.ts`) or through scripts/run_scenes.py.
import { defineScene, recordScene } from "../lib/scene.ts"

const scene = defineScene({
  name: "01-tasks",
  async run({ page, base, start, say, click, moveTo, hold }) {
    await page.goto(`${base}/tasks`)
    await page.getByRole("table", { name: "Tasks" }).waitFor()
    await page.waitForLoadState("networkidle")
    start() // the first screen is up: everything before this is trimmed
    await say("Today's tasks, overdue first.")
    // Select by role and visible text: the order of rows changes, a position would pick a different task.
    const overdue = page.getByRole("row", { name: /Send invoice/ }).first()
    await click(overdue, 900)
    const panel = page.getByRole("dialog")
    await panel.getByText("Activity").waitFor()
    await say("Each task keeps its history: who changed what, and when.")
    await moveTo(panel.getByText("Activity"))
    await hold() // keep the panel open until the caption has been read
    await page.keyboard.press("Escape")
  },
})

export default scene
if (import.meta.main) await recordScene(scene)
