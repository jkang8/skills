// Before: the component fetches, tracks loading/error, filters and renders. Testing the list needs a fake fetch.
import { useEffect, useState } from "react";

type Invoice = { id: number; customer: string; amountCents: number; paid: boolean };

export function Invoices({ customer }: { customer: string }) {
  const [rows, setRows] = useState<Invoice[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetch(`/api/customers/${customer}/invoices`)
      .then((r) => r.json())
      .then(setRows)
      .catch((e: Error) => setError(e.message));
  }, [customer]);
  if (error) return <p>{error}</p>;
  if (!rows) return <p>Loading</p>;
  return <ul>{rows.filter((r) => !r.paid).map((r) => <li key={r.id}>{(r.amountCents / 100).toFixed(2)}</li>)}</ul>;
}
