"use client";

import { useEffect, useRef } from "react";

interface Creature {
  el: HTMLVideoElement;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
}

export function FloatingCreatures() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const creatures: Creature[] = [];
    const videos = container.querySelectorAll("video");

    videos.forEach((el) => {
      const size = 120 + Math.random() * 80; // 120-200px
      const speed = 0.4 + Math.random() * 0.6; // 0.4-1.0 px/frame
      const angle = Math.random() * Math.PI * 2;

      const creature: Creature = {
        el: el as HTMLVideoElement,
        x: Math.random() * (window.innerWidth - size),
        y: Math.random() * 400, // stay in upper portion
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size,
      };

      el.style.width = `${size}px`;
      el.style.position = "absolute";
      el.style.pointerEvents = "none";
      el.style.zIndex = "5";
      el.style.transition = "none";

      creatures.push(creature);
    });

    let animId: number;
    let wobbleT = 0;

    function animate() {
      wobbleT += 0.02;
      const W = window.innerWidth;
      const H = container!.offsetHeight;

      for (const c of creatures) {
        // Add gentle wobble to velocity
        const wobbleX = Math.sin(wobbleT * 1.3 + c.size) * 0.15;
        const wobbleY = Math.cos(wobbleT * 0.9 + c.size * 0.7) * 0.2;

        c.x += c.vx + wobbleX;
        c.y += c.vy + wobbleY;

        // Bounce off edges with slight randomization
        if (c.x < -c.size * 0.3) {
          c.x = -c.size * 0.3;
          c.vx = Math.abs(c.vx) * (0.8 + Math.random() * 0.4);
          c.vy += (Math.random() - 0.5) * 0.5;
        }
        if (c.x > W - c.size * 0.7) {
          c.x = W - c.size * 0.7;
          c.vx = -Math.abs(c.vx) * (0.8 + Math.random() * 0.4);
          c.vy += (Math.random() - 0.5) * 0.5;
        }
        if (c.y < -c.size * 0.2) {
          c.y = -c.size * 0.2;
          c.vy = Math.abs(c.vy) * (0.8 + Math.random() * 0.4);
          c.vx += (Math.random() - 0.5) * 0.3;
        }
        if (c.y > H - c.size * 0.5) {
          c.y = H - c.size * 0.5;
          c.vy = -Math.abs(c.vy) * (0.8 + Math.random() * 0.4);
          c.vx += (Math.random() - 0.5) * 0.3;
        }

        // Clamp velocity so they don't get too fast
        const maxSpeed = 1.2;
        const speed = Math.sqrt(c.vx * c.vx + c.vy * c.vy);
        if (speed > maxSpeed) {
          c.vx = (c.vx / speed) * maxSpeed;
          c.vy = (c.vy / speed) * maxSpeed;
        }

        // Flip horizontally based on direction
        const flipX = c.vx < 0 ? "scaleX(-1)" : "scaleX(1)";
        c.el.style.transform = `translate(${c.x}px, ${c.y}px) ${flipX}`;
      }

      animId = requestAnimationFrame(animate);
    }

    animate();

    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 z-[5] pointer-events-none overflow-hidden"
    >
      <video autoPlay muted loop playsInline>
        <source src="/animations/butterfly_flutter.webm" type="video/webm" />
      </video>
    </div>
  );
}
