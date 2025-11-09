import { Card, CardContent } from './ui/Card';
import { Skeleton } from './ui/Skeleton';

export default function IdeaCardSkeleton() {
  return (
    <Card className="border-gray-200 animate-slide-up">
      <CardContent className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <Skeleton className="h-12 w-12 rounded-xl flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </div>

        <div className="mb-4 space-y-2.5 bg-gray-50/50 rounded-lg p-4">
          <Skeleton className="h-4 w-20 mb-3" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
            <Skeleton className="h-4 w-full" />
          </div>
        </div>

        <Skeleton className="h-20 w-full rounded-lg mb-5" />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Skeleton className="h-12 w-full rounded-md" />
          <Skeleton className="h-12 w-full rounded-md" />
        </div>
      </CardContent>
    </Card>
  );
}
