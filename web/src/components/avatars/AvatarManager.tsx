"use client";

import { useState, useEffect, useRef } from "react";
import { useSession } from "next-auth/react";
import {
  listAvatars,
  createAvatar,
  deleteAvatar,
  type Avatar,
} from "@/lib/api";
// Session is used only to gate the UI; the backend token is minted server-side
// by the Next.js proxy routes under /api/avatars/*.
import { Button } from "@/components/ui/button";
import { Plus, Upload, X, Trash2, Loader2, Sparkles } from "lucide-react";

interface AvatarManagerProps {
  /** Optional callback fired when avatars list changes (used by /create wizard). */
  onAvatarsChange?: (avatars: Avatar[]) => void;
  /** Show selectable mode (used inside /create wizard). */
  selectable?: boolean;
  selectedIds?: string[];
  onSelect?: (id: string) => void;
}

const RELATIONSHIP_OPTIONS = [
  { value: "boy", label: "Boy" },
  { value: "girl", label: "Girl" },
  { value: "father", label: "Father" },
  { value: "mother", label: "Mother" },
  { value: "grandfather", label: "Grandfather" },
  { value: "grandmother", label: "Grandmother" },
  { value: "brother", label: "Brother" },
  { value: "sister", label: "Sister" },
  { value: "uncle", label: "Uncle" },
  { value: "aunt", label: "Aunt" },
  { value: "friend", label: "Friend" },
];

export function AvatarManager({
  onAvatarsChange,
  selectable = false,
  selectedIds = [],
  onSelect,
}: AvatarManagerProps) {
  const { data: session, status } = useSession();
  const signedIn = !!session?.user?.email;

  const [avatars, setAvatars] = useState<Avatar[]>([]);
  const [quota, setQuota] = useState(3);
  const [used, setUsed] = useState(0);
  const [canCreate, setCanCreate] = useState(true);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [type, setType] = useState("boy");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function refresh() {
    if (!signedIn) return;
    setLoading(true);
    try {
      const data = await listAvatars();
      setAvatars(data.avatars);
      setQuota(data.quota);
      setUsed(data.used);
      setCanCreate(data.can_create);
      onAvatarsChange?.(data.avatars);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load avatars");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signedIn]);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setError("Photo must be under 10MB");
      return;
    }
    setError(null);
    setPhotoFile(file);
    const reader = new FileReader();
    reader.onload = () => setPhotoPreview(reader.result as string);
    reader.readAsDataURL(file);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!signedIn || !photoFile || !name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await createAvatar({ name: name.trim(), type, photo: photoFile });
      setShowForm(false);
      setName("");
      setType("boy");
      setPhotoFile(null);
      setPhotoPreview(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Avatar creation failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(avatarId: string) {
    if (!signedIn) return;
    if (!confirm("Delete this avatar? It cannot be restored.")) return;
    try {
      await deleteAvatar(avatarId);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  if (status === "loading") {
    return (
      <div className="text-center py-8 text-muted-foreground">Loading…</div>
    );
  }
  if (!signedIn) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Sign in to create avatars.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-[var(--color-warm-brown)]">
            Your Avatars
          </h2>
          <p className="text-sm text-muted-foreground">
            {used} of {quota} used · {quota - used} remaining
          </p>
        </div>
        {canCreate && !showForm && (
          <Button
            onClick={() => setShowForm(true)}
            className="gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]"
          >
            <Plus className="h-4 w-4" />
            New Avatar
          </Button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Create form */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-border rounded-2xl p-6 space-y-4 shadow-sm"
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-[var(--color-warm-brown)] flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-[var(--color-pastel-rose)]" />
              Create a new avatar
            </h3>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setName("");
                setPhotoFile(null);
                setPhotoPreview(null);
                setError(null);
              }}
              className="h-8 w-8 rounded-full hover:bg-[var(--color-pastel-cream)] flex items-center justify-center"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input
              type="text"
              required
              maxLength={100}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Aarav, Grandma Joy, Daddy"
              className="w-full px-4 py-2.5 rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-[var(--color-pastel-pink)]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Relationship / Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-[var(--color-pastel-pink)] bg-white"
            >
              {RELATIONSHIP_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Photo (clear face shot, JPG/PNG, max 10MB)
            </label>
            <div className="flex items-start gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileChange}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex-shrink-0 w-32 h-32 rounded-2xl border-2 border-dashed border-border hover:border-[var(--color-pastel-rose)] bg-[var(--color-pastel-cream)] flex flex-col items-center justify-center gap-2 transition-colors"
              >
                {photoPreview ? (
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-full object-cover rounded-2xl"
                  />
                ) : (
                  <>
                    <Upload className="h-6 w-6 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">Choose photo</span>
                  </>
                )}
              </button>
              <div className="flex-1 text-xs text-muted-foreground space-y-2">
                <p>
                  <strong>Tips for best results:</strong>
                </p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Use a clear, front-facing photo</li>
                  <li>Good lighting (natural light works best)</li>
                  <li>Single person (group photos won&apos;t work)</li>
                  <li>Avoid sunglasses or hats covering face</li>
                </ul>
              </div>
            </div>
          </div>

          <Button
            type="submit"
            disabled={submitting || !name.trim() || !photoFile}
            className="w-full gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]"
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating avatar (~30 seconds)...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Create Avatar
              </>
            )}
          </Button>
        </form>
      )}

      {/* Quota exhausted notice */}
      {!canCreate && !showForm && (
        <div className="bg-[var(--color-pastel-cream)] border border-border rounded-2xl p-4 text-center">
          <p className="text-sm text-muted-foreground mb-2">
            You&apos;ve used all {quota} of your avatar slots.
          </p>
          <p className="text-xs text-muted-foreground">
            Get 5 more avatars for $10 — coming soon.
          </p>
        </div>
      )}

      {/* Avatars grid */}
      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground mx-auto" />
        </div>
      ) : avatars.length === 0 && !showForm ? (
        <div className="text-center py-12 text-muted-foreground">
          <p className="mb-2">No avatars yet.</p>
          <p className="text-sm">
            Create one to use your child&apos;s likeness in your stories.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {avatars.map((a) => {
            const isSelected = selectedIds.includes(a.id);
            return (
              <div
                key={a.id}
                onClick={() => selectable && onSelect?.(a.id)}
                className={`relative rounded-2xl overflow-hidden bg-white border-2 shadow-sm transition-all ${
                  selectable
                    ? "cursor-pointer hover:shadow-md"
                    : ""
                } ${
                  isSelected
                    ? "border-[var(--color-pastel-rose)] ring-2 ring-[var(--color-pastel-rose)]"
                    : "border-border"
                }`}
              >
                <div className="aspect-square bg-[var(--color-pastel-cream)] flex items-center justify-center">
                  <img
                    src={a.image_url}
                    alt={`${a.name} avatar`}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="p-3">
                  <p className="font-semibold text-sm text-[var(--color-warm-brown)] truncate">
                    {a.name}
                  </p>
                  <p className="text-xs text-muted-foreground capitalize truncate">
                    {a.type}
                  </p>
                </div>
                {!selectable && (
                  <button
                    onClick={() => handleDelete(a.id)}
                    className="absolute top-2 right-2 h-7 w-7 rounded-full bg-white/90 hover:bg-red-50 flex items-center justify-center shadow-sm transition-colors"
                    aria-label="Delete avatar"
                  >
                    <Trash2 className="h-3.5 w-3.5 text-red-600" />
                  </button>
                )}
                {isSelected && (
                  <div className="absolute top-2 right-2 h-7 w-7 rounded-full bg-[var(--color-pastel-rose)] flex items-center justify-center shadow-sm text-white text-sm font-bold">
                    ✓
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
