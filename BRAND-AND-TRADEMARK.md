# Brand & Trademark Guidance — two collateral tracks

*Read before producing or sharing any deck, one-pager, or customer-forward asset. This protects the
work in front of AWS leadership, AWS Legal, and customers. The rule is simple: **never imply AWS
sponsorship or endorsement, never alter AWS marks, and never imitate AWS trade dress / look-and-feel
in customer-facing collateral.***

## The two tracks

| Track | When to use | Branding rules |
|---|---|---|
| **Internal AWS track** | AWS-internal enablement, field review, internal pitch decks | Use **AWS-approved internal templates only** (from the internal brand portal). The AWS logo and AWS visual system may appear **only** inside these approved templates and **only** for internal audiences. Do not distribute externally. |
| **Customer-safe public track** | Public repos, customer-forward decks/one-pagers, anything a customer or the open internet can see | **Neutral branding.** No AWS logo. AWS named in **plain text only** ("Built on AWS" / "runs on AWS"). A neutral color palette and layout — **not** styled to resemble AWS decks or templates. Include the not-affiliated disclaimer (below). |

**Default to the customer-safe track.** Promote an asset to the internal track only when the audience
is AWS-internal and you are using an approved internal template.

## AWS trademark rules (customer-safe track)

- **No implied sponsorship or endorsement.** Do not say or imply this is an AWS solution, AWS-endorsed,
  AWS-reviewed, or AWS-certified. (See [`NOT-CLAIMS.md`](NOT-CLAIMS.md).)
- **"Built on AWS" is text only.** Reference AWS services by their correct names in plain text. Do not
  use the AWS logo, the AWS "smile," AWS service icons, or AWS-branded templates in public collateral
  without written AWS approval.
- **Do not alter AWS marks** or combine them with this project's name to imply a joint brand.
- **Do not imitate AWS trade dress.** Avoid presenting collateral as "AWS-style," "on the AWS template,"
  or with AWS's named palette (e.g. "Squid Ink," "AWS Orange") such that it reads as official AWS
  material. A neutral dark theme is fine; describing it as an AWS design system is not.
- **Get approval before external use.** If you work at AWS, obtain internal/field approval (and Legal
  where required) before using any of this as a customer-facing asset.

## Required disclaimer (put on customer-facing collateral)

> Independent reference accelerator. Built on AWS. Not an AWS service, not AWS-supported software, not
> an official AWS solution, and not affiliated with or endorsed by Amazon Web Services. AWS and AWS
> service names are trademarks of Amazon.com, Inc. or its affiliates.

## What in this repo is which track (today)

- The generated decks under `decks/` use a **neutral dark-theme palette and a consistent professional
  layout**. Treat them as **internal-track drafts**: before any external/customer use, either (a)
  rebuild them in an AWS-approved internal template (internal audiences only), or (b) re-skin to a fully
  neutral brand with no AWS logo and the disclaimer above (customer-safe track).
- The **AWS logo is never bundled** in this repo and must not be added to customer-facing output without
  written AWS approval. Any `decks/assets/` logo slot is **internal-track only**.
- READMEs, `MATURITY.yaml`, assurance packets, SOWs, and code are customer-safe (plain-text AWS naming,
  no logo, disclaimers present).

*Colors and hex values are not trademarks; the concern is **presenting collateral as AWS's** through
logo, named palette, iconography, or "AWS template" framing. When in doubt, neutralize and add the
disclaimer.*
