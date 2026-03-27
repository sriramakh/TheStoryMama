"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, Sparkles, Crown } from "lucide-react";
import { PRICING_PLANS } from "@/lib/constants";

export function PricingCards() {
  async function handlePurchase(planId: string) {
    // TODO: Integrate Stripe checkout
    window.location.href = `/auth/signin?callbackUrl=/pricing&plan=${planId}`;
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
