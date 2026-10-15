// Netlify Function: receives website form submissions and sends them to Follow Up Boss
// as Events (https://docs.followupboss.com/reference/events-post).
//
// Required environment variable (Netlify > Site settings > Environment variables):
//   FUB_API_KEY      your Follow Up Boss API key (Admin > API)
// Optional:
//   FUB_SYSTEM       name of this lead source system   (default "militaryhomessd.com")
//   FUB_SYSTEM_KEY   X-System-Key if you registered a system with FUB
//   LEAD_SOURCE      source label shown in FUB          (default "militaryhomessd.com")

const EVENT_TYPES = {
  search: "Property Search",
  pcs_guide: "Registration",
  home_value: "Seller Inquiry",
  contact: "General Inquiry",
};

const TAGS = {
  search: ["Website", "Buyer", "Home Search Request"],
  pcs_guide: ["Website", "PCS Guide", "Relocation"],
  home_value: ["Website", "Seller", "Home Value Request", "PCS Seller"],
  contact: ["Website", "Contact Form"],
};

const json = (status, body) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

const clean = (v, max = 500) => (typeof v === "string" ? v.trim().slice(0, max) : "");

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  let d;
  try { d = await req.json(); } catch { return json(400, { error: "Invalid JSON" }); }

  // Honeypot: silently accept bots without forwarding
  if (clean(d.company)) return json(200, { ok: true });

  const firstName = clean(d.firstName, 80);
  const lastName = clean(d.lastName, 80);
  const email = clean(d.email, 200);
  const phone = clean(d.phone, 40);
  const formType = EVENT_TYPES[d.formType] ? d.formType : "contact";

  if (!firstName || !lastName || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return json(422, { error: "Missing required fields" });
  }
  if (formType === "home_value" && !clean(d.street)) return json(422, { error: "Missing address" });

  const smsConsent = d.smsConsent === true;
  const tags = [...TAGS[formType]];
  if (smsConsent) tags.push("SMS Opt-In");
  else tags.push("No SMS Consent");
  if (/va/i.test(clean(d.financing))) tags.push("VA Buyer");

  // Human-readable summary for the FUB timeline
  const details = [
    ["Form", formType],
    ["Areas", d.areas], ["Price range", d.price], ["Bedrooms", d.beds],
    ["Duty station", d.base], ["Timeline", d.timeline], ["Financing", d.financing],
    ["Plan", d.plan], ["Interest", d.interest],
    ["Property", [d.street, d.city, d.zip].filter(Boolean).join(", ")],
    ["Message", d.message],
    ["SMS consent", smsConsent ? `YES — ${new Date().toISOString()}` : "NO (do not text)"],
    ["Consent language shown", d.consentText],
    ["Page", d.pageUrl], ["Landing page", d.landing], ["Referrer", d.referrer],
    ["UTM", [d.utm_source, d.utm_medium, d.utm_campaign].filter(Boolean).join(" / ")],
  ]
    .filter(([, v]) => clean(v))
    .map(([k, v]) => `${k}: ${clean(v, 1500)}`)
    .join("\n");

  const event = {
    source: process.env.LEAD_SOURCE || "militaryhomessd.com",
    system: process.env.FUB_SYSTEM || "militaryhomessd.com",
    type: EVENT_TYPES[formType],
    message: clean(d.message, 2000) || undefined,
    description: details,
    pageUrl: clean(d.pageUrl, 500) || undefined,
    pageTitle: clean(d.pageTitle, 200) || undefined,
    person: {
      firstName,
      lastName,
      emails: [{ value: email }],
      phones: phone ? [{ value: phone }] : [],
      tags,
    },
  };

  if (formType === "home_value") {
    event.property = { street: clean(d.street), city: clean(d.city), state: "CA", code: clean(d.zip, 10) };
  }
  if (formType === "search") {
    event.propertySearch = { type: "For Sale", neighborhood: clean(d.areas) || undefined, city: clean(d.areas) || undefined };
  }

  const key = process.env.FUB_API_KEY;
  if (!key) {
    console.error("FUB_API_KEY is not set");
    return json(500, { error: "CRM not configured" });
  }

  const headers = {
    "Content-Type": "application/json",
    Authorization: "Basic " + Buffer.from(`${key}:`).toString("base64"),
    "X-System": process.env.FUB_SYSTEM || "militaryhomessd.com",
  };
  if (process.env.FUB_SYSTEM_KEY) headers["X-System-Key"] = process.env.FUB_SYSTEM_KEY;

  try {
    const r = await fetch("https://api.followupboss.com/v1/events", { method: "POST", headers, body: JSON.stringify(event) });
    // FUB returns 200/201 on success, 204 when the lead flow is set to ignore this source
    if (r.status >= 200 && r.status < 300) return json(200, { ok: true });
    console.error("FUB error", r.status, await r.text());
    return json(502, { error: "CRM rejected the lead" });
  } catch (e) {
    console.error("FUB request failed", e);
    return json(502, { error: "CRM unreachable" });
  }
};
