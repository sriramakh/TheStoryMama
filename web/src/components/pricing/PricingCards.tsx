"use client";

import { useEffect } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Sparkles, Crown } from "lucide-react";
import { PRICING_PLANS, FASTSPRING_STOREFRONT } from "@/lib/constants";

// FastSpring product path mapping
const PLAN_TO_PRODUCT: Record<string, string> = {
  pack_5: "story-pack-5",
  monthly_10: "monthly-10",
  yearly_15: "annual-15",
};

declare global {
  interface Window {
    fastspring?: {
      builder: {
        push: (config: Record<string, unknown>) => void;
        checkout: (productPath: string) => void;
        recognize: (data: Record<string, string>) => void;
      };
    };
  }
}

export function PricingCards() {
  const { data: session } = useSession();

  // Load FastSpring SBL script
  useEffect(() => {
    if (document.getElementById("fsc-api")) return;

    const script = document.createElement("script");
    script.id = "fsc-api";
    script.src = `https://sbl.onfastspring.com/sbl/1.0.3/fastspring-builder.min.js`;
    script.type = "text/javascript";
    script.dataset.storefront = FASTSPRING_STOREFRONT;
    script.dataset.accessKey = ""; // SBL doesn't need access key for popup
    script.dataset.dataPopupWebhookReceived = "onFSPopupClosed";
    document.head.appendChild(script);

    // Callback when purchase completes
    (window as unknown as Record<string, unknown>).onFSPopupClosed = function (data: unknown) {
      // Redirect to dashboard after purchase
      window.location.href = "/dashboard?purchased=true";
    };
  }, []);

  function handlePurchase(planId: string) {
    const productPath = PLAN_TO_PRODUCT[planId];
    if (!productPath) return;

    if (!session?.user) {
      window.location.href = `/auth/signin?callbackUrl=/pricing&plan=${planId}`;
      return;
    }

    // Pass user email to FastSpring for receipt
    if (window.fastspring?.builder && session.user.email) {
      window.fastspring.builder.recognize({
        email: session.user.email,
      });
    }

    // Open FastSpring popup checkout
    if (window.fastspring?.builder) {
      window.fastspring.builder.push({
        products: [{ path: productPath, quantity: 1 }],
        checkout: true,
      });
    } else {
      // Fallback: redirect to storefront
      window.open(
        `https://${FASTSPRING_STOREFRONT}/${productPath}`,
        "_blank"
      );
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
      {PRICING_PLANS.map((plan) => {
        const isPopular = "popular" in plan && plan.popular;
        const isBestValue = "bestValue" in plan && plan.bestValue;

        return (
          <Card
            key={plan.id}
            className={`relative border-0 shadow-sm hover:shadow-lg transition-shadow overflow-hidden ${
              isPopular ? "ring-2 ring-[var(--color-pastel-pink)]" : ""
            }`}
          >
            {isPopular && (
              <div className="absolute top-0 right-0">
                <Badge className="rounded-none rounded-bl-xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] border-0 px-3 py-1">
                  <Sparkles className="h-3 w-3 mr-1" />
                  Most Popular
                </Badge>
              </div>
            )}
            {isBestValue && (
              <div className="absolute top-0 right-0">
                <Badge className="rounded-none rounded-bl-xl bg-[var(--color-pastel-mint)] text-emerald-700 border-0 px-3 py-1">
                  <Crown className="h-3 w-3 mr-1" />
                  Best Value
                </Badge>
              </div>
            )}

            <CardContent className="p-6 sm:p-8">
              <h3 className="text-lg font-bold text-[var(--color-warm-brown)]">
                {plan.name}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {plan.description}
              </p>

              <div className="mt-6 flex items-baseline gap-1">
                <span className="text-4xl font-extrabold text-[var(--color-warm-brown)]">
                  ${plan.price}
                </span>
                {plan.period !== "one-time" && (
                  <span className="text-muted-foreground">/{plan.period}</span>
                )}
              </div>

              <p className="mt-1 text-sm text-muted-foreground">
                {plan.credits} stories
                {plan.period !== "one-time" ? " per month" : ""}
              </p>

              <Button
                onClick={() => handlePurchase(plan.id)}
                className={`w-full mt-6 rounded-xl py-5 ${
                  isPopular
                    ? "bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]"
                    : ""
                }`}
                variant={isPopular ? "default" : "outline"}
              >
                Get Started
              </Button>

              <ul className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center gap-2.5">
                    <div className="h-4 w-4 rounded-full bg-[var(--color-pastel-mint)] flex items-center justify-center flex-shrink-0">
                      <Check className="h-2.5 w-2.5 text-emerald-600" />
                    </div>
                    <span className="text-sm text-foreground/80">
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
