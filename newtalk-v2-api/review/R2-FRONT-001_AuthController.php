<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\ValidationException;

/**
 * R1-001 Sanctum 인증 API
 * POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me
 */
class AuthController extends Controller
{
    /**
     * POST /api/auth/login
     */
    public function login(Request $request): JsonResponse
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        if (! Auth::attempt($request->only('email', 'password'))) {
            throw ValidationException::withMessages([
                'email' => ['이메일 또는 비밀번호가 올바르지 않습니다.'],
            ]);
        }

        $user = Auth::user();
        $token = $user->createToken('auth')->plainTextToken;
        $roles = $user->getRoleNames()->toArray();

        return response()->json([
            'success' => true,
            'token' => $token,
            'user' => [
                'id' => $user->id,
                'email' => $user->email,
                'name' => $user->name ?? $user->email,
                'roles' => $roles,
            ],
        ]);
    }

    /**
     * POST /api/auth/logout
     */
    public function logout(Request $request): JsonResponse
    {
        $request->user()?->currentAccessToken()?->delete();

        return response()->json(['success' => true]);
    }

    /**
     * GET /api/auth/me
     */
    public function me(Request $request): JsonResponse
    {
        $user = $request->user();
        if (! $user) {
            return response()->json(['success' => false, 'message' => 'Unauthenticated'], 401);
        }
        $roles = $user->getRoleNames()->toArray();

        return response()->json([
            'success' => true,
            'data' => [
                'id' => $user->id,
                'email' => $user->email,
                'name' => $user->name ?? $user->email,
                'roles' => $roles,
            ],
        ]);
    }
}
