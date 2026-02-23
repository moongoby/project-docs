<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Product;
use App\Models\Wishlist;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * R2-API-001: SNS 소셜 엔진 — 찜(위시리스트) API
 * GET /api/wishlists, POST /api/wishlists/{productId}, DELETE /api/wishlists/{productId}
 */
class WishlistController extends Controller
{
    private const PER_PAGE = 20;

    /**
     * GET /api/wishlists — 내 찜 목록.
     */
    public function index(Request $request): JsonResponse
    {
        $user = $request->user();
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);

        $wishlists = Wishlist::where('user_id', $user->id)
            ->with(['product' => fn ($q) => $q->select('id', 'name', 'wholesale_price', 'retail_price', 'user_id')->with('user:id,name')])
            ->orderByDesc('id')
            ->paginate($perPage);

        $data = $wishlists->map(function ($w) {
            $p = $w->product;
            return [
                'id' => $w->id,
                'product' => $p ? [
                    'id' => $p->id,
                    'name' => $p->name,
                    'price' => $p->wholesale_price ?? $p->retail_price ?? 0,
                    'thumbnail' => null,
                    'wholesale_name' => $p->user->name ?? null,
                ] : null,
                'created_at' => $w->created_at?->toIso8601String(),
            ];
        });

        return response()->json([
            'data' => $data,
            'current_page' => $wishlists->currentPage(),
            'last_page' => $wishlists->lastPage(),
            'per_page' => $wishlists->perPage(),
        ]);
    }

    /**
     * POST /api/wishlists/{productId} — 찜 추가.
     */
    public function store(Request $request, string $productId): JsonResponse
    {
        $user = $request->user();
        $productId = (int) $productId;

        $product = Product::find($productId);
        if (! $product) {
            return response()->json(['message' => 'Product not found.'], 404);
        }

        $exists = Wishlist::where('user_id', $user->id)->where('product_id', $productId)->exists();
        if ($exists) {
            return response()->json(['message' => 'Already in wishlist.', 'wishlisted' => true], 409);
        }

        Wishlist::create(['user_id' => $user->id, 'product_id' => $productId]);

        return response()->json(['message' => 'Added to wishlist.', 'wishlisted' => true], 201);
    }

    /**
     * DELETE /api/wishlists/{productId} — 찜 해제.
     */
    public function destroy(Request $request, string $productId): JsonResponse
    {
        $user = $request->user();
        $productId = (int) $productId;

        $wishlist = Wishlist::where('user_id', $user->id)->where('product_id', $productId)->first();
        if (! $wishlist) {
            return response()->json(['message' => 'Wishlist item not found.'], 404);
        }

        $wishlist->delete();

        return response()->json(['message' => 'Removed from wishlist.', 'wishlisted' => false]);
    }
}
