/// <reference path="../.astro/types.d.ts" />

interface Window {
  trackEvent?: (name: string, params?: Record<string, unknown>) => void;
  dataLayer?: unknown[];
}