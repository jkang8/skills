// Stands in for the generated OpenAPI client.
export type Invoice = { id: number; customer: string; amountCents: number; paid: boolean };

export async function listInvoices(customer: string): Promise<Invoice[]> {
  const res = await fetch(`/api/customers/${encodeURIComponent(customer)}/invoices`);
  if (!res.ok) throw new Error(`invoices: ${res.status}`);
  return res.json();
}
