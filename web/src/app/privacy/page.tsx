import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy Policy for TheStoryMama",
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] mb-8">
          Privacy Policy
        </h1>

        <div className="prose prose-warm max-w-none space-y-6 text-[var(--color-warm-brown)]/80 text-[15px] leading-relaxed">
          <p className="text-sm text-muted-foreground">
            Last updated: March 30, 2026
          </p>

          <p>
            At TheStoryMama, we take your privacy seriously — especially because our
            users are families with young children. This policy explains what
            information we collect, how we use it, and how we protect it.
          </p>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              1. Information We Collect
            </h2>

            <h3 className="text-base font-semibold text-[var(--color-warm-brown)] mt-4 mb-2">
              Information you provide:
            </h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>
                <strong>Account information:</strong> Name and email address when you
                sign up via email or Google OAuth
              </li>
              <li>
                <strong>Payment information:</strong> Processed by FastSpring — we never
                see or store your credit card details
              </li>
              <li>
                <strong>Story preferences:</strong> Custom story descriptions you submit
                for personalized story creation
              </li>
            </ul>

            <h3 className="text-base font-semibold text-[var(--color-warm-brown)] mt-4 mb-2">
              Information collected automatically:
            </h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>
                <strong>Reading activity:</strong> Which stories you read and your
                progress, used to provide &ldquo;Continue Reading&rdquo; and recommendations
              </li>
              <li>
                <strong>Basic analytics:</strong> Pages visited, device type, and
                browser — used to improve the website experience
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              2. How We Use Your Information
            </h2>
            <ul className="list-disc pl-6 space-y-1">
              <li>To provide and maintain the Service</li>
              <li>To personalize your experience (reading recommendations, continue reading)</li>
              <li>To process payments and manage subscriptions</li>
              <li>To send you sign-in links via email (Resend)</li>
              <li>To respond to your support requests</li>
              <li>To improve our stories and website</li>
            </ul>
            <p className="mt-3">
              <strong>We do NOT:</strong>
            </p>
            <ul className="list-disc pl-6 space-y-1">
              <li>Sell your personal information to third parties</li>
              <li>Use your data for advertising</li>
              <li>Collect data from children — our Service is designed for parents</li>
              <li>Send marketing emails unless you opt in</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              3. Children&apos;s Privacy
            </h2>
            <p>
              TheStoryMama is designed for parents and caregivers to use with their
              children. We do not knowingly collect personal information from children
              under 13. Parents create accounts and manage all interactions with the
              Service. If you believe a child has provided us with personal information,
              please contact us at hello@thestorymama.club and we will delete it promptly.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              4. Third-Party Services
            </h2>
            <p>We use the following third-party services:</p>
            <ul className="list-disc pl-6 space-y-1 mt-2">
              <li>
                <strong>Google OAuth:</strong> For sign-in authentication — subject to{" "}
                <a href="https://policies.google.com/privacy" className="text-primary hover:underline" target="_blank" rel="noopener">
                  Google&apos;s Privacy Policy
                </a>
              </li>
              <li>
                <strong>FastSpring:</strong> For payment processing — subject to{" "}
                <a href="https://fastspring.com/privacy/" className="text-primary hover:underline" target="_blank" rel="noopener">
                  FastSpring&apos;s Privacy Policy
                </a>
              </li>
              <li>
                <strong>Resend:</strong> For sending sign-in emails — subject to{" "}
                <a href="https://resend.com/legal/privacy-policy" className="text-primary hover:underline" target="_blank" rel="noopener">
                  Resend&apos;s Privacy Policy
                </a>
              </li>
              <li>
                <strong>Vercel:</strong> For hosting — subject to{" "}
                <a href="https://vercel.com/legal/privacy-policy" className="text-primary hover:underline" target="_blank" rel="noopener">
                  Vercel&apos;s Privacy Policy
                </a>
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              5. Cookies
            </h2>
            <p>
              We use essential cookies only — for authentication (keeping you signed in)
              and reading progress. We do not use tracking cookies, advertising cookies,
              or third-party analytics cookies.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              6. Data Security
            </h2>
            <p>
              We protect your data using industry-standard security measures including
              HTTPS encryption, secure authentication tokens, and access controls.
              However, no method of transmission over the Internet is 100% secure.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              7. Data Retention
            </h2>
            <p>
              We retain your account information for as long as your account is active.
              If you wish to delete your account and all associated data, contact us at
              hello@thestorymama.club. Payment records are retained as required by law.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              8. Your Rights
            </h2>
            <p>You have the right to:</p>
            <ul className="list-disc pl-6 space-y-1 mt-2">
              <li>Access the personal information we hold about you</li>
              <li>Request correction of inaccurate information</li>
              <li>Request deletion of your account and data</li>
              <li>Withdraw consent for data processing</li>
              <li>Export your data in a portable format</li>
            </ul>
            <p className="mt-2">
              To exercise any of these rights, email us at{" "}
              <a href="mailto:hello@thestorymama.club" className="text-primary hover:underline">
                hello@thestorymama.club
              </a>
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              9. Changes to This Policy
            </h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify
              registered users of significant changes via email. The &ldquo;Last updated&rdquo;
              date at the top of this page indicates when the policy was last revised.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              10. Contact
            </h2>
            <p>
              For privacy questions or concerns, contact us at{" "}
              <a href="mailto:hello@thestorymama.club" className="text-primary hover:underline">
                hello@thestorymama.club
              </a>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
