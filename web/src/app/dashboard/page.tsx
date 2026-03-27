import type { Metadata } from "next";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen,
  CreditCard,
  Plus,
  Sparkles,
  Download,
} from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Manage your stories and credits",
};

export default function DashboardPage() {
  // TODO: Fetch real data with auth
  const credits = { available: 7, total: 10, plan: "Monthly" };
  const stories = [
    {
      id: "my-story-1",
      title: "Luna's Starlit Adventure",
      style: "Pixar 3D",
      scenes: 12,
      date: "Mar 24, 2026",
    },
    {
      id: "my-story-2",
      title: "The Friendly Cloud",
      style: "Soft Pastel Dream",
      scenes: 10,
      date: "Mar 20, 2026",
    },
  ];

  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
              My Dashboard
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage your stories and account
            </p>
          </div>
          <Link href="/create">
            <Button className="gap-2 rounded-xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]">
              <Plus className="h-4 w-4" />
              New Story
            </Button>
          </Link>
        </div>

        {/* Credit balance */}
        <Card className="border-0 shadow-sm mb-8 bg-gradient-to-r from-[var(--color-pastel-lavender)]/30 to-[var(--color-pastel-pink)]/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Story Credits
                </p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-4xl font-extrabold text-[var(--color-warm-brown)]">
                    {credits.available}
                  </span>
                  <span className="text-muted-foreground">
                    of {credits.total} remaining
                  </span>
                </div>
                <Badge
                  variant="secondary"
                  className="mt-2 bg-white/60 text-[var(--color-warm-brown)]"
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  {credits.plan} Plan
                </Badge>
              </div>
              <div className="hidden sm:block">
                <Link href="/pricing">
                  <Button
                    variant="outline"
                    className="rounded-xl gap-2 bg-white/60"
                  >
                    <CreditCard className="h-4 w-4" />
                    Buy More Credits
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* My stories */}
        <div>
          <h2 className="text-xl font-bold text-[var(--color-warm-brown)] mb-4">
            My Stories
          </h2>

          {stories.length === 0 ? (
            <Card className="border-0 shadow-sm">
              <CardContent className="p-12 text-center">
                <BookOpen className="h-12 w-12 text-muted-foreground/30 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-[var(--color-warm-brown)] mb-2">
                  No stories yet
                </h3>
                <p className="text-muted-foreground mb-6">
                  Create your first personalized story!
                </p>
                <Link href="/create">
                  <Button className="gap-2 rounded-xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]">
                    <Sparkles className="h-4 w-4" />
                    Create a Story
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {stories.map((story) => (
                <Card key={story.id} className="border-0 shadow-sm">
                  <CardContent className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-14 w-14 rounded-xl bg-[var(--color-pastel-cream)] flex items-center justify-center flex-shrink-0">
                        <BookOpen className="h-6 w-6 text-[var(--color-warm-brown)]/40" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-[var(--color-warm-brown)]">
                          {story.title}
                        </h3>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs text-muted-foreground">
                            {story.style}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {story.scenes} scenes
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {story.date}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link href={`/stories/${story.id}`}>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="rounded-lg gap-1"
                        >
                          <BookOpen className="h-4 w-4" />
                          <span className="hidden sm:inline">Read</span>
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="rounded-lg gap-1"
                      >
                        <Download className="h-4 w-4" />
                        <span className="hidden sm:inline">PDF</span>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
