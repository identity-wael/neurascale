import { LRUCache } from 'lru-cache';

type Options = {
  uniqueTokenPerInterval?: number;
  interval?: number;
};

export function rateLimit(options?: Options) {
  const tokenCache = new LRUCache({
    max: options?.uniqueTokenPerInterval || 500,
    ttl: options?.interval || 60000, // 60 seconds default
  });

  return {
    check: (res: Response, limit: number, token: string) =>
      new Promise<void>((resolve, reject) => {
        const tokenCount = (tokenCache.get(token) as number[]) || [0];
        const currentUsage = tokenCount[0];

        if (currentUsage >= limit) {
          reject(new Error('Rate limit exceeded'));
        } else {
          tokenCount[0] = currentUsage + 1;
          tokenCache.set(token, tokenCount);
          resolve();
        }
      }),
  };
}
