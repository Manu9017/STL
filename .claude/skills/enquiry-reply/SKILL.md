---
name: enquiry-reply
description: Draft a reply to a SHIVAS customer enquiry (website form, WhatsApp text the user pastes, email in Gmail, or a lead from the visitor log) - work out the division and product, ask for the missing technical facts, point to the right product page, calculator and 3D model, and save it as a Gmail draft for the owner to check. Use when the user says reply to this enquiry, draft a response, follow up this lead, answer this customer, or check new enquiries in the inbox.
---

# Replying to an enquiry

## Rules
- **Draft only.** Save replies with Gmail `create_draft`, or give the text in chat. Never send, forward or label mail unless the owner asks for that exact action.
- **Never quote prices, delivery times, capacities, references or guarantees the owner hasn't given.** Engineering numbers come only from the site's own pages and calculators, and are stated as typical.
- **Leads are personal data.** Don't paste customer details into any other service, and don't copy anyone outside SHIVAS.
- Write **SHIVAS** in capitals. Keep the tone short, plain and engineer to engineer. Write English unless the customer wrote in Hindi; then reply in Hindi, with technical terms in English.

## Steps
1. **Find the enquiry.**
   - Gmail: search the inbox for `subject:"Website enquiry"`, `from:` the customer, or the subject the user gives.
   - Visitor log: the Leads tab, or the lead email from the Apps Script.
   - WhatsApp: the user pastes the text.
2. **Classify it,** using the product pages for wording:
   - Galvanizing: `galvanizing.html` and `items/` pages such as kettle, furnace, turnkey, zfe, flux.
   - Wire drawing: `wire-drawing.html`, `items/slm`, `oto`, `dbc`, `hdgwire`.
   - SHIVAS Reinplast (tanks, scrubbers, pickling, ETP/ZLD): `reinplast.html` and `items/r-*`. Reinplast enquiries go to info@shivasasia.com.
   - FRP profiles and resins: `pultrusion.html`.
3. **Ask only for what's missing.** Three to five questions at most:
   - Galvanizing: what they galvanize, tonnage per month, largest article (L × W × H, weight), steel type and silicon if known, fuel available (PNG/LPG/diesel/electric), site size, timeline.
   - Wire drawing: input rod size and grade, finished sizes, production per day, product (GI wire, nails, ACSR…), line speed, existing equipment.
   - Reinplast: chemical and concentration, temperature, volume or flow, indoor/outdoor, pollution board requirement, site.
   - FRP: profile, size, length, quantity, application.
4. **Point them somewhere useful** (one or two links with full `https://www.shivastechnology.com/...` URLs):
   - the matching product page;
   - the plant calculator (`calculator.html`) or `calculators.html#wire` / `#scrubber`;
   - the 3D model if one exists (`v/hdg-plant.html`, `v/spin-galvanizing.html`, `v/etp-zld-compact.html`, …).
5. **Sign off.** Use the name the owner gives. Then: SHIVAS Technology Limited (or SHIVAS Reinplast Company of India) · +91 98109 20468 (call/WhatsApp) · info@shivastechnology.com · A-1/270, Swadeshi Compound, Kavi Nagar Industrial Area, Ghaziabad 201002.
6. **Report back.** Show the owner the draft and say which facts are still unknown. Offer a reminder in Google Calendar to follow up in 3 working days, and only create it if the owner says yes.

For a full proposal or deck, use the installed `b2b-sales-enablement:sales-proposal-builder`, with the same rules on numbers.
