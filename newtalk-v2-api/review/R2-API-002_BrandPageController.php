<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\BrandPage;
use App\Models\Follow;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

/**
 * R2-API-002: 브랜드 페이지 API
 * GET /api/brands, GET /api/brands/{slug}, GET /api/brands/{slug}/products,
 * GET /api/brands/{slug}/feed, POST /api/brands/{slug}/follow, PUT /api/brands/me
 */
class BrandPageController extends Controller
{
    private const PER_PAGE = 20;

    /**
     * GET /api/brands — 브랜드 목록 (공개, 페이지네이션, 검색 ?q=).
     */
    public function index(Request $request): JsonResponse
    {
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);
        $q = $request->input('q', '');

        $query = BrandPage::query()
            ->active()
            ->select(['id', 'user_id', 'brand_name', 'slug', 'logo_url', 'follower_count', 'product_count'])
            ->orderByDesc('follower_count');

        if ($q !== '') {
            $query->where(function ($q2) use ($q) {
                $q2->where('brand_name', 'like', '%' . $q . '%')
                    ->orWhere('slug', 'like', '%' . $q . '%');
            });
        }

        $paginator = $query->paginate($perPage);
        $data = $paginator->getCollection()->map(fn ($b) => [
            'id' => $b->id,
            'brand_name' => $b->brand_name,
            'slug' => $b->slug,
            'logo_url' => $b->logo_url,
            'follower_count' => (int) $b->follower_count,
            'product_count' => (int) $b->product_count,
        ])->all();

        return response()->json([
            'data' => $data,
            'current_page' => $paginator->currentPage(),
            'last_page' => $paginator->lastPage(),
            'per_page' => $paginator->perPage(),
            'total' => $paginator->total(),
        ]);
    }

    /**
     * GET /api/brands/{slug} — 브랜드 상세 (공개).
     */
    public function show(Request $request, string $slug): JsonResponse
    {
        $brand = BrandPage::query()
            ->active()
            ->where('slug', $slug)
            ->withCount([])
            ->first();

        if (! $brand) {
            return response()->json(['message' => 'Brand not found.'], 404);
        }

        $brand->load([
            'products' => fn ($q) => $q->where('status', 'active')->orderByDesc('created_at')->limit(20)->with(['images' => fn ($q2) => $q2->orderBy('sort_order')->orderBy('id')->limit(1)]),
            'feedItems' => fn ($q) => $q->active()->published()->orderByDesc('published_at')->limit(10),
        ]);
        $brand->load(['feedItems.author:id,name', 'feedItems.product:id,name,wholesale_price']);

        $isFollowing = false;
        if ($request->user()) {
            $isFollowing = Follow::where('follower_id', $request->user()->id)
                ->where('following_id', $brand->user_id)
                ->exists();
        }

        $products = $brand->products->map(function ($p) {
            $firstImg = $p->relationLoaded('images') && $p->images->isNotEmpty() ? $p->images->first() : null;
            return [
                'id' => $p->id,
                'name' => $p->name,
                'price' => $p->retail_price ?? $p->wholesale_price ?? 0,
                'thumbnail' => $firstImg ? url($firstImg->path) : null,
            ];
        });
        $feedItems = $brand->feedItems->map(fn ($f) => [
            'id' => $f->id,
            'title' => $f->title,
            'media_url' => $f->media_url,
            'media_type' => $f->media_type,
            'published_at' => $f->published_at?->toIso8601String(),
            'author' => $f->author ? ['id' => $f->author->id, 'name' => $f->author->name] : null,
            'product' => $f->product ? ['id' => $f->product->id, 'name' => $f->product->name] : null,
        ]);

        $payload = [
            'id' => $brand->id,
            'user_id' => $brand->user_id,
            'brand_name' => $brand->brand_name,
            'slug' => $brand->slug,
            'logo_url' => $brand->logo_url,
            'cover_url' => $brand->cover_url,
            'description' => $brand->description,
            'business_info' => $brand->business_info,
            'sns_links' => $brand->sns_links,
            'is_active' => $brand->is_active,
            'follower_count' => (int) $brand->follower_count,
            'product_count' => (int) $brand->product_count,
            'is_following' => $isFollowing,
            'products' => $products->values()->all(),
            'feed_items' => $feedItems->values()->all(),
        ];
        return response()->json(['data' => $payload]);
    }

    /**
     * GET /api/brands/{slug}/products — 브랜드 상품 목록 (공개, cursor 페이지네이션).
     */
    public function products(Request $request, string $slug): JsonResponse
    {
        $brand = BrandPage::query()->active()->where('slug', $slug)->first();
        if (! $brand) {
            return response()->json(['message' => 'Brand not found.'], 404);
        }

        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);
        $cursor = $request->input('cursor');
        $category = $request->input('category');
        $minPrice = $request->input('min_price');
        $maxPrice = $request->input('max_price');

        $query = $brand->products()
            ->where('status', 'active')
            ->with(['images' => fn ($q) => $q->orderBy('sort_order')->orderBy('id')->limit(1)])
            ->orderByDesc('created_at');

        if ($category !== null && $category !== '') {
            $query->where('name', 'like', '%' . $category . '%');
        }
        if (is_numeric($minPrice)) {
            $query->where(function ($q) use ($minPrice) {
                $q->where('retail_price', '>=', (int) $minPrice)
                    ->orWhere('wholesale_price', '>=', (int) $minPrice);
            });
        }
        if (is_numeric($maxPrice)) {
            $query->where(function ($q) use ($maxPrice) {
                $q->where('retail_price', '<=', (int) $maxPrice)
                    ->orWhere('wholesale_price', '<=', (int) $maxPrice);
            });
        }

        $paginator = $query->cursorPaginate($perPage, ['id', 'user_id', 'name', 'retail_price', 'wholesale_price', 'created_at'], 'cursor', $cursor);

        $data = $paginator->getCollection()->map(function ($p) {
            $firstImage = $p->relationLoaded('images') && $p->images->isNotEmpty() ? $p->images->first() : null;
            return [
                'id' => $p->id,
                'name' => $p->name,
                'price' => $p->retail_price ?? $p->wholesale_price ?? 0,
                'thumbnail' => $firstImage ? url($firstImage->path) : null,
            ];
        })->all();

        return response()->json([
            'data' => $data,
            'next_cursor' => $paginator->nextCursor()?->encode(),
            'has_more' => $paginator->hasMorePages(),
        ]);
    }

    /**
     * GET /api/brands/{slug}/feed — 브랜드 피드 (공개, cursor 페이지네이션).
     */
    public function feed(Request $request, string $slug): JsonResponse
    {
        $brand = BrandPage::query()->active()->where('slug', $slug)->first();
        if (! $brand) {
            return response()->json(['message' => 'Brand not found.'], 404);
        }

        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);
        $cursor = $request->input('cursor');

        $query = $brand->feedItems()
            ->active()
            ->published()
            ->with(['author:id,name', 'product:id,name,wholesale_price'])
            ->orderByDesc('published_at');

        $paginator = $query->cursorPaginate($perPage, ['*'], 'cursor', $cursor);
        $user = $request->user();
        $feedIds = $paginator->pluck('id')->toArray();
        $likedIds = $user ? DB::table('feed_likes')->where('user_id', $user->id)->whereIn('feed_item_id', $feedIds)->pluck('feed_item_id')->flip()->toArray() : [];

        $data = $paginator->getCollection()->map(function ($item) use ($likedIds) {
            $author = $item->relationLoaded('author') ? $item->author : null;
            $product = $item->relationLoaded('product') ? $item->product : null;
            return [
                'id' => $item->id,
                'type' => $item->type,
                'title' => $item->title,
                'description' => $item->description,
                'media_url' => $item->media_url,
                'media_type' => $item->media_type,
                'author' => $author ? ['id' => $author->id, 'name' => $author->name, 'profile_image' => $author->profile_image ?? null] : null,
                'product' => $product ? [
                    'id' => $product->id,
                    'name' => $product->name,
                    'price' => $product->wholesale_price ?? $product->retail_price ?? 0,
                    'thumbnail' => null,
                ] : null,
                'like_count' => (int) $item->like_count,
                'comment_count' => (int) $item->comment_count,
                'view_count' => (int) $item->view_count,
                'is_liked' => isset($likedIds[$item->id]),
                'published_at' => $item->published_at?->toIso8601String(),
                'created_at' => $item->created_at?->toIso8601String(),
            ];
        })->all();

        return response()->json([
            'data' => $data,
            'next_cursor' => $paginator->nextCursor()?->encode(),
            'has_more' => $paginator->hasMorePages(),
        ]);
    }

    /**
     * POST /api/brands/{slug}/follow — 팔로우 토글 (인증 필수).
     */
    public function toggleFollow(Request $request, string $slug): JsonResponse
    {
        $brand = BrandPage::query()->active()->where('slug', $slug)->first();
        if (! $brand) {
            return response()->json(['message' => 'Brand not found.'], 404);
        }

        $userId = $brand->user_id;
        $currentUser = $request->user();
        if ($userId === $currentUser->id) {
            return response()->json(['message' => 'Cannot follow your own brand.'], 422);
        }

        return DB::transaction(function () use ($currentUser, $userId, $brand) {
            $follow = Follow::where('follower_id', $currentUser->id)->where('following_id', $userId)->lockForUpdate()->first();
            $wasFollowing = (bool) $follow;

            if ($follow) {
                $follow->delete();
                $brand->decrement('follower_count');
                return response()->json([
                    'following' => false,
                    'follower_count' => (int) $brand->fresh()->follower_count,
                ]);
            }

            Follow::create(['follower_id' => $currentUser->id, 'following_id' => $userId]);
            $brand->increment('follower_count');
            return response()->json([
                'following' => true,
                'follower_count' => (int) $brand->fresh()->follower_count,
            ]);
        });
    }

    /**
     * PUT /api/brands/me — 내 브랜드 수정 (wholesale만, 없으면 자동 생성).
     */
    public function updateMine(Request $request): JsonResponse
    {
        $user = $request->user();
        if (! $user->hasAnyRole(['wholesale', 'admin'])) {
            return response()->json(['message' => 'Only wholesale or admin can manage brand page.'], 403);
        }

        $validated = $request->validate([
            'brand_name' => 'nullable|string|max:255',
            'logo_url' => 'nullable|string|max:2048',
            'cover_url' => 'nullable|string|max:2048',
            'description' => 'nullable|string',
            'business_info' => 'nullable|array',
            'sns_links' => 'nullable|array',
            'sns_links.instagram' => 'nullable|string|max:2048',
            'sns_links.youtube' => 'nullable|string|max:2048',
        ]);

        $brand = BrandPage::where('user_id', $user->id)->first();
        if (! $brand) {
            $slug = Str::slug($validated['brand_name'] ?? $user->name, '-');
            $base = $slug;
            $i = 0;
            while (BrandPage::where('slug', $slug)->exists()) {
                $slug = $base . '-' . (++$i);
            }
            $brand = BrandPage::create([
                'user_id' => $user->id,
                'brand_name' => $validated['brand_name'] ?? $user->name,
                'slug' => $slug,
                'logo_url' => $validated['logo_url'] ?? null,
                'cover_url' => $validated['cover_url'] ?? null,
                'description' => $validated['description'] ?? null,
                'business_info' => $validated['business_info'] ?? null,
                'sns_links' => $validated['sns_links'] ?? null,
                'is_active' => true,
            ]);
        } else {
            if (isset($validated['brand_name'])) {
                $validated['slug'] = Rule::unique('brand_pages')->ignore($brand->id);
                // slug는 변경 시에만 재생성 (요청서에는 slug 수정 없음)
            }
            $brand->update(array_filter($validated, fn ($v) => $v !== null || in_array($v, ['description', 'business_info', 'sns_links'], true)));
        }

        $brand->refresh();
        return response()->json([
            'id' => $brand->id,
            'user_id' => $brand->user_id,
            'brand_name' => $brand->brand_name,
            'slug' => $brand->slug,
            'logo_url' => $brand->logo_url,
            'cover_url' => $brand->cover_url,
            'description' => $brand->description,
            'business_info' => $brand->business_info,
            'sns_links' => $brand->sns_links,
            'follower_count' => (int) $brand->follower_count,
            'product_count' => (int) $brand->product_count,
        ]);
    }
}
