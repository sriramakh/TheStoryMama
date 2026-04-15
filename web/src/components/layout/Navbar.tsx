"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { useSession, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Menu, Heart, User, LogOut, BookOpen } from "lucide-react";

const navLinks = [
  { href: "/library", label: "Story Library" },
  { href: "/series", label: "Story Series" },
  { href: "/create", label: "Create a Story" },
];

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { data: session } = useSession();
  const user = session?.user;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <Image
            src="/logo.png"
            alt="TheStoryMama"
            width={36}
            height={36}
            className="rounded-lg transition-transform group-hover:scale-110"
          />
          <span className="text-xl font-bold tracking-tight text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            TheStoryMama
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="px-4 py-2 rounded-lg text-sm font-medium text-foreground/70 hover:text-foreground hover:bg-[var(--color-pastel-cream)] transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Desktop auth */}
        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger className="flex items-center gap-2 rounded-full px-3 py-1.5 hover:bg-[var(--color-pastel-cream)] transition-colors outline-none">
                <div className="h-8 w-8 rounded-full bg-[var(--color-pastel-pink)] flex items-center justify-center text-sm font-bold text-[var(--color-warm-brown)]">
                  {user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || "U"}
                </div>
                <span className="text-sm font-medium text-[var(--color-warm-brown)] max-w-[120px] truncate">
                  {user.name || user.email?.split("@")[0]}
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <Link href="/dashboard">
                  <DropdownMenuItem className="cursor-pointer gap-2">
                    <BookOpen className="h-4 w-4" />
                    My Stories
                  </DropdownMenuItem>
                </Link>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => signOut({ callbackUrl: "/" })}
                  className="cursor-pointer gap-2 text-red-600"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Link href="/auth/signin">
              <Button variant="ghost" size="sm" className="gap-2">
                <User className="h-4 w-4" />
                Sign In
              </Button>
            </Link>
          )}
          <Link href="/create">
            <Button
              size="sm"
              className="gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] shadow-sm"
            >
              <Heart className="h-4 w-4" />
              Create Story
            </Button>
          </Link>
        </div>

        {/* Mobile menu */}
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger className="md:hidden inline-flex items-center justify-center h-9 w-9 rounded-md hover:bg-accent">
            <Menu className="h-5 w-5" />
          </SheetTrigger>
          <SheetContent side="right" className="w-72 bg-background">
            <div className="flex flex-col gap-4 mt-8">
              {/* User info on mobile */}
              {user && (
                <div className="flex items-center gap-3 px-4 pb-2">
                  <div className="h-10 w-10 rounded-full bg-[var(--color-pastel-pink)] flex items-center justify-center text-lg font-bold text-[var(--color-warm-brown)]">
                    {user.name?.[0]?.toUpperCase() || "U"}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[var(--color-warm-brown)]">
                      {user.name || "Welcome!"}
                    </p>
                    <p className="text-xs text-muted-foreground truncate max-w-[160px]">
                      {user.email}
                    </p>
                  </div>
                </div>
              )}

              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="px-4 py-3 rounded-xl text-base font-medium hover:bg-[var(--color-pastel-cream)] transition-colors"
                >
                  {link.label}
                </Link>
              ))}

              {user && (
                <Link
                  href="/dashboard"
                  onClick={() => setMobileOpen(false)}
                  className="px-4 py-3 rounded-xl text-base font-medium hover:bg-[var(--color-pastel-cream)] transition-colors"
                >
                  My Stories
                </Link>
              )}

              <div className="border-t border-border my-2" />

              {user ? (
                <Button
                  variant="outline"
                  className="w-full gap-2"
                  onClick={() => {
                    setMobileOpen(false);
                    signOut({ callbackUrl: "/" });
                  }}
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </Button>
              ) : (
                <Link href="/auth/signin" onClick={() => setMobileOpen(false)}>
                  <Button variant="outline" className="w-full gap-2">
                    <User className="h-4 w-4" />
                    Sign In
                  </Button>
                </Link>
              )}

              <Link href="/create" onClick={() => setMobileOpen(false)}>
                <Button className="w-full gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]">
                  <Heart className="h-4 w-4" />
                  Create Story
                </Button>
              </Link>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
