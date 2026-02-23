import { fetchApi } from "./api";
import { getMockExplore, getMockFeed } from "./mock-feed";
import type { FeedItem, FeedResponse } from "@/types/feed";

const USE_MOCK = false;

type FeedApiRaw = { data: FeedItem[]; next_cursor: string | null; per_page?: number };

export async function getFeed(cursor?: string): Promise<FeedResponse> {
  if (USE_MOCK) return getMockFeed(cursor);
  const res = (await fetchApi(`feed${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`)) as unknown as FeedApiRaw;
  return { data: res.data, next_cursor: res.next_cursor ?? null, has_more: !!res.next_cursor };
}

export async function getExplore(
  type?: string,
  cursor?: string
): Promise<FeedResponse> {
  if (USE_MOCK) return getMockExplore(type, cursor);
  const params = new URLSearchParams();
  if (type) params.set("type", type);
  if (cursor) params.set("cursor", cursor);
  const qs = params.toString();
  const res = (await fetchApi(`feed/explore${qs ? `?${qs}` : ""}`)) as unknown as FeedApiRaw;
  return { data: res.data, next_cursor: res.next_cursor ?? null, has_more: !!res.next_cursor };
}

export async function toggleLike(
  feedId: number
): Promise<{ is_liked: boolean; like_count: number }> {
  if (USE_MOCK)
    return { is_liked: true, like_count: Math.floor(Math.random() * 100) };
  const res = await fetchApi<{ is_liked: boolean; like_count: number }>(
    `feed/${feedId}/like`,
    { method: "POST" }
  );
  return res.data;
}

export async function toggleWishlist(
  productId: number
): Promise<{ wishlisted: boolean }> {
  if (USE_MOCK) return { wishlisted: true };
  const res = await fetchApi<{ wishlisted: boolean }>(
    `wishlists/${productId}`,
    { method: "POST" }
  );
  return res.data;
}
