"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { formatPrice, formatRelativeTime } from "@/lib/date-utils";
import { toggleLike, toggleWishlist } from "@/lib/feed-api";
import type { FeedItem } from "@/types/feed";
import {
  Heart,
  MessageCircle,
  Send,
  Bookmark,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface FeedCardProps {
  item: FeedItem;
  onLikeToggle?: (feedId: number, isLiked: boolean, likeCount: number) => void;
}

export function FeedCard({ item, onLikeToggle }: FeedCardProps) {
  const [isLiked, setIsLiked] = useState(item.is_liked);
  const [likeCount, setLikeCount] = useState(item.like_count);
  const [showMore, setShowMore] = useState(false);

  async function handleLike() {
    try {
      const res = await toggleLike(item.id);
      setIsLiked(res.is_liked);
      setLikeCount(res.like_count);
      onLikeToggle?.(item.id, res.is_liked, res.like_count);
    } catch {
      // optimistic rollback 생략
    }
  }

  async function handleWishlist() {
    if (!item.product) return;
    try {
      await toggleWishlist(item.product.id);
    } catch {
      // no-op
    }
  }

  const description =
    item.description && !showMore && item.description.length > 60
      ? `${item.description.slice(0, 60)}...`
      : item.description;

  return (
    <Card className="mx-auto w-full max-w-lg overflow-hidden border-0 bg-white shadow-none">
      {/* 상단: 도매 프로필 */}
      <CardHeader className="flex flex-row items-center gap-3 p-4 pb-2">
        <Avatar className="h-10 w-10">
          <AvatarImage
            src={item.author.profile_image ?? undefined}
            alt={item.author.name}
          />
          <AvatarFallback>
            {item.author.name.slice(0, 2).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <p className="truncate font-medium text-zinc-900">
            {item.author.name}
          </p>
          <p className="text-xs text-zinc-500">
            {formatRelativeTime(item.published_at)}
          </p>
        </div>
        <Button variant="outline" size="sm" className="shrink-0 rounded-full">
          팔로우
        </Button>
      </CardHeader>

      {/* 미디어 */}
      <div className="relative w-full bg-zinc-100">
        {item.media_type === "video" && item.media_url ? (
          <video
            src={item.media_url}
            className="aspect-[4/5] w-full object-cover"
            controls
            playsInline
          />
        ) : (
          <img
            src={item.media_url ?? "https://picsum.photos/400/500"}
            alt={item.title}
            className="aspect-[4/5] w-full object-cover"
          />
        )}
      </div>

      {/* 하단 액션바 */}
      <CardContent className="space-y-2 p-4 pt-3">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={handleLike}
            className="flex items-center gap-1.5 text-zinc-700 hover:text-zinc-900"
            aria-label={isLiked ? "좋아요 취소" : "좋아요"}
          >
            <Heart
              className={cn("h-6 w-6", isLiked && "fill-red-500 text-red-500")}
            />
          </button>
          <button
            type="button"
            className="flex items-center gap-1.5 text-zinc-700 hover:text-zinc-900"
            aria-label="댓글"
          >
            <MessageCircle className="h-6 w-6" />
          </button>
          <button
            type="button"
            className="flex items-center gap-1.5 text-zinc-700 hover:text-zinc-900"
            aria-label="공유"
          >
            <Send className="h-6 w-6" />
          </button>
          {item.product && (
            <button
              type="button"
              onClick={handleWishlist}
              className="ml-auto text-zinc-700 hover:text-zinc-900"
              aria-label="찜"
            >
              <Bookmark className="h-6 w-6" />
            </button>
          )}
        </div>

        {likeCount > 0 && (
          <p className="text-sm font-medium text-zinc-900">
            좋아요 {likeCount}개
          </p>
        )}
        <div className="space-y-0.5">
          <p className="text-sm font-medium text-zinc-900">{item.title}</p>
          {description && (
            <p className="text-sm text-zinc-600">
              {description}
              {item.description &&
                item.description.length > 60 &&
                !showMore && (
                  <button
                    type="button"
                    onClick={() => setShowMore(true)}
                    className="ml-1 text-zinc-500 hover:underline"
                  >
                    더보기
                  </button>
                )}
            </p>
          )}
        </div>
      </CardContent>

      {/* 상품 정보 카드 */}
      {item.product && (
        <CardFooter className="border-t border-zinc-100 p-4">
          <Link
            href={`/retail/product/${item.product.id}`}
            className="flex w-full items-center gap-3 rounded-lg border border-zinc-200 bg-zinc-50 p-3 transition hover:bg-zinc-100"
          >
            {item.product.thumbnail && (
              <img
                src={item.product.thumbnail}
                alt=""
                className="h-14 w-14 rounded object-cover"
              />
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-zinc-900">
                {item.product.name}
              </p>
              <p className="text-xs text-zinc-500">
                {item.product.wholesale_name} · {formatPrice(item.product.price)}
              </p>
            </div>
            <span className="flex items-center gap-1 text-sm font-medium text-zinc-700">
              사입하기
              <ChevronRight className="h-4 w-4" />
            </span>
          </Link>
        </CardFooter>
      )}
    </Card>
  );
}
