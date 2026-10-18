import { Button } from "@/components/ui/button";
export function Settings() {
  return <section className="flex flex-col gap-4 rounded-lg border border-border bg-background">
    <h1 className="text-xl font-medium">Settings</h1>
    <kbd>⌘K</kbd>
    <Button>Save</Button>
  </section>;
}
