import { fetchApi } from "./api";
import type {
  BrandListItem,
  BrandPage,
  BrandProductListItem,
  BrandListResponse,
  BrandProductsResponse,
} from "@/types/brand";
import type { FeedItem } from "@/types/feed";

export async function getBrands(
  q?: string,
  cursor?: string
): Promise<{ data: BrandListItem[]; next_cursor: string | null; has_more: boolean }> {
  const page = cursor ? parseInt(cursor, 10) || 1 : 1;
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  params.set("page", String(page));
  const res = await fetchApi<BrandListResponse>(`brands?${params.toString()}`);
  const body = res as unknown as BrandListResponse;
  const nextPage = body.current_page < body.last_page ? body.current_page + 1 : null;
  return {
    data: body.data,
    next_cursor: nextPage != null ? String(nextPage) : null,
    has_more: body.current_page < body.last_page,
  };
}

export async function getBrand(slug: string): Promise<BrandPage> {
  const res = await fetchApi<BrandPage>(`brands/${encodeURIComponent(slug)}`);
  return (res as unknown as { data?: BrandPage }).data ?? (res as unknown as BrandPage);
}

export async function getBrandProducts(
  slug: string,
  cursor?: string
): Promise<{ data: BrandProductListItem[]; next_cursor: string | null; has_more: boolean }> {
  const params = new URLSearchParams();
  if (cursor) params.set("cursor", cursor);
  const qs = params.toString();
  const res = await fetchApi<BrandProductsResponse>(
    `brands/${encodeURIComponent(slug)}/products${qs ? `?${qs}` : ""}`
  );
  const body = res as unknown as BrandProductsResponse;
  return {
    data: body.data,
    next_cursor: body.next_cursor ?? null,
    has_more: body.has_more ?? false,
  };
}

export async function getBrandFeed(
  slug: string,
  cursor?: string
): Promise<{ data: FeedItem[]; next_cursor: string | null; has_more: boolean }> {
  const params = new URLSearchParams();
  if (cursor) params.set("cursor", cursor);
  const qs = params.toString();
  const res = await fetchApi<{ data: FeedItem[]; next_cursor: string | null; has_more: boolean }>(
    `brands/${encodeURIComponent(slug)}/feed${qs ? `?${qs}` : ""}`
  );
  return {
    data: res.data.data ?? res.data,
    next_cursor: res.data.next_cursor ?? null,
    has_more: res.data.has_more ?? false,
  };
}

export async function toggleBrandFollow(
  slug: string
): Promise<{ following: boolean; follower_count: number }> {
  const res = await fetchApi<{ following: boolean; follower_count: number }>(
    `brands/${encodeURIComponent(slug)}/follow`,
    { method: "POST" }
  );
  return res.data;
}
