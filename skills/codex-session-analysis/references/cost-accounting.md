# Cost comparison

Fetch the exact model's current official API pricing/model pages and, for Codex credits, the separate Codex pricing page. Use an available official-docs capability when present; this skill does not depend on another locally installed skill. Record the fetched URL, retrieval date, rate tier, currency/unit, promotions, and applicable context thresholds. Prefer `developers.openai.com/api/docs/pricing`, the exact model page, and `developers.openai.com/codex/pricing`.

Do not freeze model rates into this skill. If a model or rate cannot be verified, mark it unavailable instead of substituting a similar model. Current rates produce a current-rate estimate, not necessarily the historical invoice.

For zero separately billed cache writes and uniform applicable rates per million tokens:

```text
estimated cost = ((input - cached input) * input rate
                  + cached input * cached rate
                  + output * output rate) / 1,000,000
```

Calculate per request when context thresholds, model switches, tier changes, or differing rates apply. A session's cumulative tokens exceeding a long-context threshold does not make its requests long-context. Validate cache-write accounting against the log schema and official billing rule before adding it; avoid charging the same write as both ordinary input and a full extra write fee.

Show input, cached-input, and output cost contributions. Mark estimated rather than observed tiers when `service_tier` is absent. Separate region uplifts, paid tools, tax, discounts, and subscription inclusions as applicable; do not introduce unsupported adjustments. A rate limit or plan field alone is not evidence of dollar charges.

Codex credits have their own rate card and speed multipliers. Compute them separately; never infer a credits-to-dollar purchase exchange rate from coincidentally proportional rate tables. API Fast/priority pricing and Codex Fast credits need not share a multiplier.

Use unrounded values for comparisons:

```text
A savings relative to B = 1 - cost_A / cost_B
B premium relative to A = cost_B / cost_A - 1
```

Token ratios are not cost ratios. Explain which contribution drives the difference. Weighted-token break-even analysis is optional and only valid under its stated rate relationships. Keep per-run rows visible when averaging; with one run per model, report the actual runs rather than describing a stable model average.
