<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Follow;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/**
 * R2-API-001: SNS 소셜 엔진 — 팔로우 API
 * POST /api/follows/{userId}, DELETE /api/follows/{userId},
 * GET /api/follows/{userId}/followers, GET /api/follows/{userId}/following
 */
class FollowController extends Controller
{
    private const PER_PAGE = 20;

    /**
     * POST /api/follows/{userId} — 팔로우.
     */
    public function follow(Request $request, string $userId): JsonResponse
    {
        $currentUser = $request->user();
        $targetId = (int) $userId;

        if ($targetId === $currentUser->id) {
            return response()->json(['message' => 'Cannot follow yourself.'], 422);
        }

        $target = User::find($targetId);
        if (! $target) {
            return response()->json(['message' => 'User not found.'], 404);
        }

        $exists = Follow::where('follower_id', $currentUser->id)->where('following_id', $targetId)->exists();
        if ($exists) {
            return response()->json(['message' => 'Already following.', 'following' => true], 409);
        }

        Follow::create(['follower_id' => $currentUser->id, 'following_id' => $targetId]);

        return response()->json(['message' => 'Followed.', 'following' => true]);
    }

    /**
     * DELETE /api/follows/{userId} — 언팔로우.
     */
    public function unfollow(Request $request, string $userId): JsonResponse
    {
        $currentUser = $request->user();
        $targetId = (int) $userId;

        $follow = Follow::where('follower_id', $currentUser->id)->where('following_id', $targetId)->first();
        if (! $follow) {
            return response()->json(['message' => 'Follow relationship not found.'], 404);
        }

        $follow->delete();

        return response()->json(['message' => 'Unfollowed.', 'following' => false]);
    }

    /**
     * GET /api/follows/{userId}/followers — 팔로워 목록.
     */
    public function followers(Request $request, string $userId): JsonResponse
    {
        $targetId = (int) $userId;
        $currentUser = $request->user();
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);

        $follows = Follow::where('following_id', $targetId)
            ->with('follower:id,name')
            ->paginate($perPage);

        $followerIds = $follows->pluck('follower_id')->toArray();
        $followingByMe = $currentUser->id !== $targetId
            ? Follow::where('follower_id', $currentUser->id)->whereIn('following_id', $followerIds)->pluck('following_id')->flip()->toArray()
            : [];

        $data = $follows->map(function ($f) use ($followingByMe) {
            $u = $f->follower;
            return [
                'user' => [
                    'id' => $u->id,
                    'name' => $u->name,
                    'profile_image' => $u->profile_image ?? null,
                ],
                'is_following' => isset($followingByMe[$u->id]),
            ];
        });

        return response()->json([
            'data' => $data,
            'current_page' => $follows->currentPage(),
            'last_page' => $follows->lastPage(),
            'per_page' => $follows->perPage(),
        ]);
    }

    /**
     * GET /api/follows/{userId}/following — 팔로잉 목록.
     */
    public function following(Request $request, string $userId): JsonResponse
    {
        $targetId = (int) $userId;
        $currentUser = $request->user();
        $perPage = (int) $request->input('per_page', self::PER_PAGE);
        $perPage = min(max($perPage, 1), 100);

        $follows = Follow::where('follower_id', $targetId)
            ->with('following:id,name')
            ->paginate($perPage);

        $followingIds = $follows->pluck('following_id')->toArray();
        $followingByMe = $currentUser->id !== $targetId
            ? Follow::where('follower_id', $currentUser->id)->whereIn('following_id', $followingIds)->pluck('following_id')->flip()->toArray()
            : [];

        $data = $follows->map(function ($f) use ($followingByMe) {
            $u = $f->following;
            return [
                'user' => [
                    'id' => $u->id,
                    'name' => $u->name,
                    'profile_image' => $u->profile_image ?? null,
                ],
                'is_following' => isset($followingByMe[$u->id]),
            ];
        });

        return response()->json([
            'data' => $data,
            'current_page' => $follows->currentPage(),
            'last_page' => $follows->lastPage(),
            'per_page' => $follows->perPage(),
        ]);
    }
}
