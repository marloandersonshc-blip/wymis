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
  var form = document.querySelector("form.inquiry");
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

  // Partner CTA clicks (only recorded when analytics is enabled)
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href$="partner"]');
    if (a) track("partner_cta_click", { link_text: (a.textContent || "").trim().slice(0, 60), page_path: location.pathname });
  });

  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
