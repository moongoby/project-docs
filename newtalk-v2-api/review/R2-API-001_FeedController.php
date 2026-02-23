<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\FeedItem;
use App\Models\FeedLike;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

/**
 * R2-API-001: SNS 소셜 엔진 — 피드 API
 * GET /api/feed, GET /api/feed/explore, GET /api/feed/{id}, POST /api/feed,
 * POST /api/feed/{id}/like, GET /api/feed/search
 */
class FeedController extends Controller
{
    private const PER_PAGE = 20;

    private const FEED_TYPES = ['product', 'content', 'story', 'shorts'];

    /**
     * GET /api/feed — 홈 피드 (인증 필수). 팔로우 70% + 인기 30% 혼합, cursor 페이지네이션.
     */
    public function index(Request $request): JsonResponse
    {
        $user = $request->user();
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);
        $cursor = $request->input('cursor');

        $followingIds = $user->followings()->pluck('following_id')->toArray();

        $query = FeedItem::query()
            ->active()
            ->published();

        if (! empty($followingIds)) {
            $ids = implode(',', array_map('intval', $followingIds));
            $query->orderByRaw('(feed_items.user_id IN (' . $ids . ')) DESC');
        }
        $query->orderByDesc(DB::raw('(feed_items.like_count + feed_items.view_count)'))
            ->orderByDesc('feed_items.published_at')
            ->orderByDesc('feed_items.id');

        $paginator = $query->with(['author:id,name', 'product:id,name,supply_price,retail_price'])
            ->cursorPaginate($perPage, ['*'], 'cursor', $cursor);

        $feedIds = $paginator->pluck('id')->toArray();
        $likedIds = $user->feedLikes()->whereIn('feed_item_id', $feedIds)->pluck('feed_item_id')->flip()->toArray();

        $data = $paginator->map(fn ($item) => $this->formatFeedItem($item, isset($likedIds[$item->id])))->values()->all();

        return response()->json([
            'data' => $data,
            'next_cursor' => $paginator->nextCursor()?->encode(),
            'per_page' => $perPage,
        ]);
    }

    /**
     * GET /api/feed/explore — 탐색 (인증 선택). 비인증 시 is_liked 없음.
     */
    public function explore(Request $request): JsonResponse
    {
        $user = auth('sanctum')->user();
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);
        $type = $request->input('type');
        $category = $request->input('category');

        $query = FeedItem::query()
            ->active()
            ->published()
            ->with(['author:id,name', 'product:id,name,supply_price,retail_price'])
            ->orderByDesc(DB::raw('like_count + view_count'));

        if ($type && in_array($type, self::FEED_TYPES, true)) {
            $query->where('type', $type);
        }
        if ($category !== null && $category !== '') {
            $query->whereHas('product', fn ($q) => $q->where('name', 'like', '%' . $category . '%'));
        }

        $paginator = $query->cursorPaginate($perPage);
        $feedIds = $paginator->pluck('id')->toArray();
        $likedIds = $user ? $user->feedLikes()->whereIn('feed_item_id', $feedIds)->pluck('feed_item_id')->flip()->toArray() : [];

        $data = $paginator->map(fn ($item) => $this->formatFeedItem($item, isset($likedIds[$item->id])))->values()->all();

        return response()->json([
            'data' => $data,
            'next_cursor' => $paginator->nextCursor()?->encode(),
            'per_page' => $perPage,
        ]);
    }

    /**
     * GET /api/feed/{id} — 피드 상세. view_count 1 증가.
     */
    public function show(Request $request, string $id): JsonResponse
    {
        $item = FeedItem::query()
            ->active()
            ->published()
            ->with(['author:id,name', 'product:id,name,supply_price,retail_price'])
            ->find((int) $id);

        if (! $item) {
            return response()->json(['message' => 'Feed item not found.'], 404);
        }

        $item->increment('view_count');
        $item->refresh();
        $user = $request->user();
        $isLiked = $user ? $user->feedLikes()->where('feed_item_id', $item->id)->exists() : false;

        return response()->json($this->formatFeedItem($item, $isLiked, true));
    }

    /**
     * POST /api/feed — 피드 작성 (wholesale, admin만).
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'type' => 'required|in:' . implode(',', self::FEED_TYPES),
            'title' => 'required|string|max:255',
            'description' => 'nullable|string',
            'media_url' => 'nullable|string|max:2048',
            'media_type' => 'nullable|in:image,video',
            'product_id' => 'nullable|integer|exists:products,id',
            'published_at' => 'nullable|date',
        ]);

        $user = $request->user();
        $validated['user_id'] = $user->id;
        $validated['published_at'] = $validated['published_at'] ?? now();
        $validated['is_active'] = true;

        $item = FeedItem::create($validated);
        $item->load(['author:id,name', 'product:id,name,supply_price,retail_price']);

        return response()->json($this->formatFeedItem($item, false, true), 201);
    }

    /**
     * POST /api/feed/{id}/like — 좋아요 토글.
     */
    public function toggleLike(Request $request, string $id): JsonResponse
    {
        $feedItem = FeedItem::active()->published()->find((int) $id);
        if (! $feedItem) {
            return response()->json(['message' => 'Feed item not found.'], 404);
        }

        $user = $request->user();

        return DB::transaction(function () use ($user, $feedItem) {
            $like = FeedLike::where('user_id', $user->id)->where('feed_item_id', $feedItem->id)->first();

            if ($like) {
                $like->delete();
                $feedItem->decrement('like_count');
                return response()->json(['is_liked' => false, 'like_count' => (int) $feedItem->fresh()->like_count]);
            }

            FeedLike::create(['user_id' => $user->id, 'feed_item_id' => $feedItem->id]);
            $feedItem->increment('like_count');
            return response()->json(['is_liked' => true, 'like_count' => (int) $feedItem->fresh()->like_count]);
        });
    }

    /**
     * GET /api/feed/search?q= — 피드 검색 (title, description LIKE).
     */
    public function search(Request $request): JsonResponse
    {
        $q = $request->input('q', '');
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);
        $cursor = $request->input('cursor');

        $query = FeedItem::query()
            ->active()
            ->published()
            ->with(['author:id,name', 'product:id,name,supply_price,retail_price'])
            ->when($q !== '', fn ($query) => $query->where(function ($q2) use ($q) {
                $q2->where('title', 'like', '%' . $q . '%')
                    ->orWhere('description', 'like', '%' . $q . '%');
            }))
            ->orderByDesc('published_at');

        $paginator = $query->cursorPaginate($perPage, ['*'], 'cursor', $cursor);
        $user = $request->user();
        $feedIds = $paginator->pluck('id')->toArray();
        $likedIds = $user ? $user->feedLikes()->whereIn('feed_item_id', $feedIds)->pluck('feed_item_id')->flip()->toArray() : [];

        $data = $paginator->map(fn ($item) => $this->formatFeedItem($item, isset($likedIds[$item->id])))->values()->all();

        return response()->json([
            'data' => $data,
            'next_cursor' => $paginator->nextCursor()?->encode(),
            'per_page' => $perPage,
        ]);
    }

    private function formatFeedItem(FeedItem $item, bool $isLiked = false, bool $full = false): array
    {
        $author = $item->relationLoaded('author') ? $item->author : null;
        $product = $item->relationLoaded('product') ? $item->product : null;
        $base = [
            'id' => $item->id,
            'type' => $item->type,
            'title' => $item->title,
            'description' => $item->description,
            'media_url' => $item->media_url,
            'media_type' => $item->media_type,
            'author' => $author ? [
                'id' => $author->id,
                'name' => $author->name,
                'profile_image' => $author->profile_image ?? null,
            ] : null,
            'product' => $product ? [
                'id' => $product->id,
                'name' => $product->name,
                'price' => $product->supply_price ?? $product->retail_price ?? 0,
                'thumbnail' => null,
            ] : null,
            'like_count' => (int) $item->like_count,
            'comment_count' => (int) $item->comment_count,
            'view_count' => (int) $item->view_count,
            'is_liked' => $isLiked,
            'published_at' => $item->published_at?->toIso8601String(),
            'created_at' => $item->created_at?->toIso8601String(),
        ];
        if ($full) {
            $base['is_pinned'] = $item->is_pinned;
            $base['is_active'] = $item->is_active;
            $base['product_id'] = $item->product_id;
        }
        return $base;
    }
}
