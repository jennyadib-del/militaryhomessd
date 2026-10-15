# militaryhomessd.com — Jenny Adib, San Diego Military Realtor

Static website + a Netlify Function that sends every form lead into Follow Up Boss.

## 1. Fill in your details (required before launch)
Open `build.py` and edit the `CONFIG` block at the top:

| Setting | What to put |
|---|---|
| `AGENT_DRE` | Your CA DRE salesperson license # |
| `PHONE` / `PHONE_TEL` | Display phone, and digits-only version (e.g. `+16195551234`) |
| `EMAIL` | Your business email |
| `LEGAL_BUSINESS_NAME` | **Must match exactly** the business name on your FUB texting (10DLC) registration / Tax ID |
| `BROKERAGE_ADDRESS` | Real Broker's office address on file with the DRE |
| `INSTAGRAM` / `FACEBOOK` / `LINKEDIN` | Optional profile URLs |

Then rebuild:

```
python3 build.py
```

## 2. Deploy on Netlify (free)
1. Create a Netlify account → **Add new site → Deploy manually** is easiest for a first test, but to use the Follow Up Boss function, connect a GitHub repo (or use the Netlify CLI: `netlify deploy --prod`). Build settings come from `netlify.toml`.
2. **Site settings → Environment variables** → add `FUB_API_KEY` (Follow Up Boss → Admin → API → create key).
3. **Domain management** → add `militaryhomessd.com`. Netlify shows the DNS records to add in **GoDaddy → DNS** (an A record for `@` and a CNAME for `www`). HTTPS is automatic.

## 3. Follow Up Boss
Each form creates a FUB Event:

| Form | FUB event type | Tags |
|---|---|---|
| Search VA-Friendly Homes | Property Search | Website, Buyer, Home Search Request |
| Free San Diego PCS Guide | Registration | Website, PCS Guide, Relocation |
| What's My Military Home Worth | Seller Inquiry | Website, Seller, Home Value Request, PCS Seller |
| Contact | General Inquiry | Website, Contact Form |

Every lead is also tagged **SMS Opt-In** or **No SMS Consent**, and the timeline note records the exact consent text shown plus a timestamp. Use the tag to keep non-consenting leads out of text action plans.

Optional: paste your FUB Pixel snippet where marked in `build.py` (search "Follow Up Boss Pixel").

### Website compliance answers for the FUB registration form
- **Privacy Policy URL:** `https://militaryhomessd.com/privacy-policy/` — states mobile numbers and opt-in data are never sold/shared with third parties for marketing.
- **Terms and Conditions URL:** `https://militaryhomessd.com/terms/` — includes the SMS Terms section (program, frequency, rates, STOP/HELP, carrier disclaimer).
- **Opt-in language:** on every form that collects a phone number. Phone is optional and the SMS checkbox is optional and unchecked, so no one has to agree to texts to submit.

## 4. Editing content
- Pages: `src/pages/*.html` (header comment = title, meta description, URL, hero text)
- Blog posts: add a new file in `src/blog/` (copy an existing post; set `date`, `path`, `h1`, `excerpt`)
- Forms: `{{form:search}}`, `{{form:pcs_guide}}`, `{{form:home_value}}`, `{{form:contact}}`
- Styles: `public/assets/css/site.css`. Scripts: `public/assets/js/site.js`
- An IDX search widget can be pasted into `src/pages/military-homes-for-sale-san-diego.html` (marked comment).

## SEO page map
| Page | URL | Keyword |
|---|---|---|
| Homepage | `/` | San Diego Military Realtor |
| VA Loan Buyers | `/va-loan-realtor-san-diego/` | VA Loan Realtor San Diego |
| PCS Relocation Guide | `/pcs-to-san-diego/` | PCS to San Diego |
| Military Home Search | `/military-homes-for-sale-san-diego/` | Military Homes for Sale San Diego |
| VA Loan Assumptions | `/va-assumable-homes-san-diego/` | VA Assumable Homes San Diego |
| Military Home Sellers | `/sell-home-during-pcs-san-diego/` | Sell Home During PCS San Diego |
| Military Base Housing | `/homes-near-san-diego-military-bases/` | Homes Near San Diego Military Bases |
| VA Loan Education | `/va-loan-benefits-california/` | VA Loan Benefits California |
| Neighborhood Guide | `/best-places-to-live-near-naval-base-san-diego/` | Best Places to Live Near Naval Base San Diego |
| About Jenny | `/about-jenny/` | San Diego Veteran Realtor |

After launch, submit `https://militaryhomessd.com/sitemap.xml` in Google Search Console and set up a Google Business Profile.
