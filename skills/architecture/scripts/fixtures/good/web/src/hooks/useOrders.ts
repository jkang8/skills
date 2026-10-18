import { getOrders } from "../api/client";
import type { Row } from "../components/OrderList";
export function useOrders(): Promise<Row[]> { return getOrders().then((xs) => xs.map((n) => ({ n }))); }
