import { fetchApi } from "./api";
import type { ProductDetail, ProductListItem } from "@/types/product";

const USE_MOCK = true; // API 완성 후 false로 변경

function getBaseUrl(): string {
  if (typeof window === "undefined") return "";
  return window.location.origin;
}

/** GET /api/products/{id} */
export async function getProduct(id: number): Promise<ProductDetail> {
  if (USE_MOCK) return getMockProduct(id);
  const res = await fetchApi<ProductDetail>(`products/${id}`);
  return res.data;
}

/** GET /api/products/{id}/related 또는 GET /api/products?limit=8 */
export async function getRelatedProducts(id: number): Promise<ProductListItem[]> {
  if (USE_MOCK) return getMockRelatedProducts(id);
  try {
    const res = await fetchApi<ProductListItem[]>(`products/${id}/related`);
    return res.data ?? [];
  } catch {
    const res = await fetchApi<ProductListItem[]>(`products?limit=8`);
    return res.data ?? [];
  }
}

/** POST /api/wishlists/{productId}/toggle */
export async function toggleProductWishlist(
  productId: number
): Promise<{ wishlisted: boolean }> {
  const res = await fetchApi<{ wishlisted: boolean }>(
    `wishlists/${productId}/toggle`,
    { method: "POST" }
  );
  return res.data;
}

/** 공유: navigator.share 또는 클립보드 복사 */
export async function shareProduct(id: number): Promise<{ url: string }> {
  const url = `${getBaseUrl()}/retail/product/${id}`;
  const title = "뉴톡 상품";
  const text = "이 상품을 확인해 보세요.";

  if (typeof navigator !== "undefined" && navigator.share) {
    await navigator.share({
      title,
      text,
      url,
    });
    return { url };
  }
  await navigator.clipboard.writeText(url);
  return { url };
}

// --- Mock (USE_MOCK 시 사용) ---
function getMockProduct(id: number): ProductDetail {
  return {
    id,
    name: "24SS 린넨 와이드 팬츠",
    description:
      "시즌 시즌감 있는 린넨 소재로 제작된 와이드 실루엣 팬츠입니다. 도매가 대비 합리적인 가격에 만나보세요.",
    supply_price: 25000,
    retail_price: 45000,
    wholesale_price: 35000,
    category_id: 1,
    category_name: "팬츠",
    images: [
      {
        id: 1,
        url: `https://picsum.photos/600/800?random=${id}`,
        sort_order: 0,
      },
      {
        id: 2,
        url: `https://picsum.photos/600/800?random=${id + 1}`,
        sort_order: 1,
      },
    ],
    options: [
      { id: 1, color: "블랙", size: "S", stock: 10, price_diff: 0 },
      { id: 2, color: "블랙", size: "M", stock: 0, price_diff: 0 },
      { id: 3, color: "베이지", size: "S", stock: 5, price_diff: 2000 },
    ],
    author: {
      id: 1,
      name: "블레스유",
      profile_image: "https://picsum.photos/80/80?random=1",
    },
    is_wishlisted: false,
    wishlist_count: 42,
    feed_count: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
}

function getMockRelatedProducts(_productId: number): ProductListItem[] {
  return Array.from({ length: 6 }, (_, i) => ({
    id: 100 + i,
    name: ["오버핏 크롭 자켓", "베이직 코튼 티셔츠", "하이웨이스트 슬랙스", "데님 스커트", "니트 가디건", "울 블렌드 코트"][i]!,
    supply_price: 20000 + i * 5000,
    retail_price: 38000 + i * 4000,
    thumbnail: `https://picsum.photos/200/200?random=${100 + i}`,
    author_name: "블레스유",
    is_wishlisted: false,
  }));
}
