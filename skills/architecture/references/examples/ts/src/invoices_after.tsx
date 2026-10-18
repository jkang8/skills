// After: a hook owns the I/O and its states; the list is a pure component over typed props.
import { useEffect, useState } from "react";
import { listInvoices, type Invoice } from "./api";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; invoices: Invoice[] };

export function useInvoices(customer: string): State {
  const [state, setState] = useState<State>({ kind: "loading" });
  useEffect(() => {
    let live = true;
    listInvoices(customer)
      .then((invoices) => live && setState({ kind: "ready", invoices }))
      .catch((e: Error) => live && setState({ kind: "error", message: e.message }));
    return () => { live = false; };
  }, [customer]);
  return state;
}

export function UnpaidList({ invoices }: { invoices: Invoice[] }) {
  return <ul>{invoices.filter((i) => !i.paid).map((i) => <li key={i.id}>{(i.amountCents / 100).toFixed(2)}</li>)}</ul>;
}

export function Invoices({ customer }: { customer: string }) {
  const s = useInvoices(customer);
  if (s.kind === "error") return <p>{s.message}</p>;
  if (s.kind === "loading") return <p>Loading</p>;
  return <UnpaidList invoices={s.invoices} />;
}
