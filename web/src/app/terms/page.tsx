import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Terms of Service for TheStoryMama",
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] mb-8">
          Terms of Service
        </h1>

        <div className="prose prose-warm max-w-none space-y-6 text-[var(--color-warm-brown)]/80 text-[15px] leading-relaxed">
          <p className="text-sm text-muted-foreground">
            Last updated: March 30, 2026
          </p>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              1. Acceptance of Terms
            </h2>
            <p>
              By accessing and using TheStoryMama (&ldquo;the Service&rdquo;), operated at
              www.thestorymama.club, you agree to be bound by these Terms of Service.
              If you do not agree to these terms, please do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              2. Description of Service
            </h2>
            <p>
              TheStoryMama provides illustrated children&apos;s bedtime stories for
              personal, non-commercial use. The Service includes:
            </p>
            <ul className="list-disc pl-6 space-y-1 mt-2">
              <li>A free library of illustrated stories available to all visitors</li>
              <li>Personalized story creation for registered and paid users</li>
              <li>Downloadable PDF storybooks</li>
              <li>Story sharing features</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              3. User Accounts
            </h2>
            <p>
              To access certain features, you may need to create an account. You are
              responsible for maintaining the confidentiality of your account credentials
              and for all activities that occur under your account. You must provide
              accurate and complete information when creating your account.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              4. Payments and Subscriptions
            </h2>
            <p>
              Paid features are processed through FastSpring, our authorized payment
              processor. By making a purchase, you agree to FastSpring&apos;s terms of
              service. All prices are displayed in your local currency where available.
            </p>
            <ul className="list-disc pl-6 space-y-1 mt-2">
              <li>One-time story packs do not expire</li>
              <li>Monthly subscriptions renew automatically and can be cancelled anytime</li>
              <li>Annual subscriptions renew automatically at the end of each year</li>
              <li>Refunds are handled on a case-by-case basis — contact us at hello@thestorymama.club</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              5. Content and Intellectual Property
            </h2>
            <p>
              All stories, illustrations, and content on TheStoryMama are owned by
              TheStoryMama or its licensors. You may:
            </p>
            <ul className="list-disc pl-6 space-y-1 mt-2">
              <li>Read stories online for personal, non-commercial use</li>
              <li>Download PDF storybooks for personal use</li>
              <li>Share story links with friends and family</li>
            </ul>
            <p className="mt-2">You may not:</p>
            <ul className="list-disc pl-6 space-y-1 mt-2">
              <li>Reproduce, distribute, or sell any content commercially</li>
              <li>Use content to train AI models or for data mining</li>
              <li>Remove watermarks, credits, or attribution from content</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              6. User Conduct
            </h2>
            <p>
              When using the custom story creation feature, you agree not to submit
              descriptions that are harmful, offensive, inappropriate for children,
              or violate any applicable laws. We reserve the right to refuse or remove
              content that violates these guidelines.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              7. Availability and Modifications
            </h2>
            <p>
              We strive to keep TheStoryMama available at all times but do not guarantee
              uninterrupted access. We may modify, suspend, or discontinue any part of
              the Service at any time. We will make reasonable efforts to notify users of
              significant changes.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              8. Limitation of Liability
            </h2>
            <p>
              TheStoryMama is provided &ldquo;as is&rdquo; without warranties of any kind. We are
              not liable for any indirect, incidental, or consequential damages arising
              from your use of the Service. Our total liability is limited to the amount
              you paid for the Service in the 12 months preceding the claim.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              9. Governing Law
            </h2>
            <p>
              These terms are governed by the laws of India. Any disputes shall be
              resolved in the courts of Bangalore, Karnataka, India.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mt-8 mb-3">
              10. Contact
            </h2>
            <p>
              For questions about these terms, contact us at{" "}
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
