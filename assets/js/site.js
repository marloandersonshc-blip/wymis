(function () {
  // Sends an analytics event when GA4 is loaded; does nothing otherwise
  function track(name, params) { if (typeof window.gtag === "function") window.gtag("event", name, params || {}); }

  // Mobile menu
  var btn = document.getElementById("menuBtn");
  var links = document.getElementById("navLinks");
  if (btn && links) {
    var setMenu = function (open) {
      links.dataset.open = open ? "true" : "false";
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    };
    btn.addEventListener("click", function () { setMenu(links.dataset.open !== "true"); });
    links.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
  }

  // Delivery format toggle (curriculum transcript)
  var segBtns = document.querySelectorAll(".seg button[data-fmt]");
  if (segBtns.length) {
    var apply = function (f) {
      segBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.fmt === f ? "true" : "false"); });
      document.querySelectorAll(".tx-fmt").forEach(function (el) {
        el.querySelector("b").textContent = el.dataset[f + "Time"];
        el.querySelector("span").textContent = el.dataset[f + "Label"];
      });
      document.querySelectorAll(".fmt[data-fmt]").forEach(function (c) { c.dataset.active = c.dataset.fmt === f ? "true" : "false"; });
    };
    segBtns.forEach(function (b) { b.addEventListener("click", function () { apply(b.dataset.fmt); }); });
  }

  // Inquiry form: client-side checks and result message after contact.php redirects back
  var form = document.querySelector("form.inquiry:not(.register)");
  if (form) {
    var note = form.querySelector(".form-note");
    var params = new URLSearchParams(window.location.search);
    var showMsg = function (cls, text) {
      var m = document.createElement("div");
      m.className = "form-msg " + cls;
      m.setAttribute("role", "status");
      m.textContent = text;
      form.prepend(m);
    };
    if (params.get("sent") === "1") {
      showMsg("ok", "Thank you. Your inquiry was sent and we will follow up within two business days.");
      track("generate_lead", { form_name: "partner_inquiry" });
    }
    if (params.get("error") === "1") showMsg("err", "Your inquiry could not be sent. Check that your name and email are filled in, then try again.");
    if (params.get("error") === "2") showMsg("err", "Our mail service did not respond. Please try again in a few minutes or email us directly.");
    form.addEventListener("submit", function (e) {
      var name = form.elements.name, email = form.elements.email;
      if (!name.value.trim()) { e.preventDefault(); note.textContent = "Add your name so we know who to reply to."; name.focus(); return; }
      if (!email.value.trim() || !email.checkValidity()) { e.preventDefault(); note.textContent = "Enter a valid email address so we can reply."; email.focus(); }
    });
  }

  // Intensive dates: mark past events closed (local date), shared by every page that lists them
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var isPast = function (iso) { var p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]) < today; };
  // Promo banner: show the next upcoming intensive, or hide the banner when none are left
  var promo = document.getElementById("promo");
  if (promo) {
    var next = null;
    promo.querySelectorAll(".promo-link").forEach(function (a) {
      var up = !isPast(a.dataset.date) && !next;
      if (up) next = a;
      a.hidden = !up;
    });
    if (!next) promo.hidden = true;
  }
  document.querySelectorAll(".event[data-date]").forEach(function (card) {
    if (!isPast(card.dataset.date)) return;
    card.classList.add("is-past");
    var b = card.querySelector(".event-btn"); if (b) b.remove();
    var c = card.querySelector(".event-closed"); if (c) c.hidden = false;
  });
  document.querySelectorAll('.event-strip a[href*="event="]').forEach(function (a) {
    var m = a.href.match(/(\d{4}-\d{2}-\d{2})/); if (m && isPast(m[1])) a.parentNode.remove();
  });

  // Registration form
  var reg = document.querySelector("form.register");
  if (reg) {
    var rp = new URLSearchParams(window.location.search);
    var sel = reg.elements.event, ageSel = reg.elements.age, guard = document.getElementById("guardian");
    var rnote = reg.querySelector(".form-note");
    Array.prototype.forEach.call(sel.options, function (o) {
      var m = o.value.match(/(\d{4}-\d{2}-\d{2})$/);
      if (m && isPast(m[1])) { o.disabled = true; o.textContent += " (closed)"; }
    });
    var pick = function (slug) {
      var o = Array.prototype.find.call(sel.options, function (x) { return x.value === slug && !x.disabled; });
      if (o) { sel.value = slug; sel.dispatchEvent(new Event("change")); }
    };
    if (rp.get("event")) pick(rp.get("event"));
    document.querySelectorAll(".event-btn[data-event]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        if (location.pathname.replace(/\/$/, "").endsWith("/register")) {
          e.preventDefault(); pick(a.dataset.event);
          document.getElementById("register").scrollIntoView({ behavior: "smooth" });
          setTimeout(function () { reg.elements.first.focus({ preventScroll: true }); }, 450);
        }
      });
    });
    var syncGuard = function () {
      var minor = ageSel.value === "16 or 17";
      guard.hidden = !minor;
      reg.elements.gname.required = minor; reg.elements.gemail.required = minor; reg.elements.gconsent.required = minor;
    };
    ageSel.addEventListener("change", syncGuard); syncGuard();
    var offerBox = document.getElementById("senior-offer");
    var syncOffer = function () {
      var o = sel.options[sel.selectedIndex];
      var on = !!(o && o.dataset.offer);
      offerBox.hidden = !on;
      if (!on) reg.elements.offer.checked = false;
    };
    if (offerBox) { sel.addEventListener("change", syncOffer); syncOffer(); }
    var rmsg = function (cls, text) {
      var m = document.createElement("div");
      m.className = "form-msg " + cls; m.setAttribute("role", "status"); m.textContent = text;
      reg.prepend(m);
    };
    var done = rp.get("registered");
    if (done) {
      var o = Array.prototype.find.call(sel.options, function (x) { return x.value === done; });
      rmsg("ok", "You're registered" + (o ? " for " + o.textContent.replace(" (closed)", "") : "") + ". Check your email for your confirmation (and your spam folder, just in case)." + (rp.get("consent") === "parent" ? " We also emailed your parent or guardian the consent form. They need to sign it before the event." : ""));
      track("sign_up", { method: "intensive_registration", event_slug: done });
    }
    var errs = { "1": "Your registration could not be sent. Check the city, your name, email, and age, then try again.",
                 "2": "Our mail service did not respond. Please try again in a few minutes or email us directly.",
                 "3": "Registrants under 18 need a parent or guardian name and email, and the box checked. Please add those and try again.",
                 "4": "Registration for that date has closed. Please choose another city." };
    if (errs[rp.get("error")]) rmsg("err", errs[rp.get("error")]);
    reg.addEventListener("submit", function (e) {
      var bad = function (el, text) { e.preventDefault(); rnote.textContent = text; el.focus(); };
      var em = reg.elements.email;
      if (!sel.value) return bad(sel, "Choose the city and date you want to attend.");
      if (!reg.elements.first.value.trim()) return bad(reg.elements.first, "Add your first name.");
      if (!reg.elements.last.value.trim()) return bad(reg.elements.last, "Add your last name.");
      if (!em.value.trim() || !em.checkValidity()) return bad(em, "Enter a valid email address for your confirmation.");
      if (!ageSel.value) return bad(ageSel, "Select your age.");
      if (ageSel.value === "16 or 17") {
        if (!reg.elements.gname.value.trim()) return bad(reg.elements.gname, "Add your parent or guardian's name.");
        if (!reg.elements.gemail.value.trim() || !reg.elements.gemail.checkValidity()) return bad(reg.elements.gemail, "Add a valid parent or guardian email.");
        if (!reg.elements.gconsent.checked) return bad(reg.elements.gconsent, "Confirm that your parent or guardian knows you are registering.");
      }
    });
  }

  // Consent form: relationship field only applies when a parent or guardian signs
  var cf = document.querySelector("form.consent");
  if (cf && cf.elements.minor) {
    var relBox = cf.querySelector("[data-minor-only]");
    var syncRel = function () { if (relBox) relBox.hidden = cf.elements.minor.value === "no"; };
    cf.elements.minor.addEventListener("change", syncRel); syncRel();
  }
  if (document.querySelector(".consent-done")) track("consent_signed", {});

  // Flyer lightbox (native <dialog>: Esc closes, focus is trapped and restored by the browser)
  document.querySelectorAll("[data-flyer]").forEach(function (btn) {
    var dlg = document.getElementById(btn.dataset.flyer);
    if (!dlg || typeof dlg.showModal !== "function") return;
    btn.addEventListener("click", function () {
      var im = dlg.querySelector("img[data-src]");
      if (im && !im.getAttribute("src")) im.src = im.dataset.src;
      dlg.showModal();
      document.documentElement.classList.add("lb-open");
      track("view_flyer", { flyer: btn.dataset.flyer });
    });
    dlg.querySelector(".lb-close").addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target.classList.contains("lb-body")) dlg.close(); });
    dlg.addEventListener("close", function () { document.documentElement.classList.remove("lb-open"); });
    dlg.querySelectorAll("a[download]").forEach(function (a) {
      a.addEventListener("click", function () { track("file_download", { file_name: a.getAttribute("href").split("/").pop() }); });
    });
  });

  // Partner CTA clicks (only recorded when analytics is enabled)
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href$="partner"]');
    if (a) track("partner_cta_click", { link_text: (a.textContent || "").trim().slice(0, 60), page_path: location.pathname });
  });

  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
