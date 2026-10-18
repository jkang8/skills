import { Slot } from "@radix-ui/react-slot";
export function Button(props: { asChild?: boolean }) {
  const C = props.asChild ? Slot : "button";
  return <C className="rounded-md bg-primary text-primary-foreground transition-[transform,opacity] duration-150 active:scale-[0.97]" />;
}
