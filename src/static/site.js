/* jeskridge.com hub — theme toggle, mobile nav, gallery lightbox. */
(function () {
  "use strict";

  var root = document.documentElement;
  try { var s = localStorage.getItem("je-theme"); if (s) root.setAttribute("data-theme", s); } catch (e) {}

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".theme-toggle");
    if (!btn) return;
    var dark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("je-theme", next); } catch (err) {}
  });

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // Lightbox for galleries
  var shots = document.querySelectorAll(".shot");
  if (shots.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.innerHTML = '<img alt="">';
    document.body.appendChild(box);
    var img = box.querySelector("img");
    shots.forEach(function (btn) {
      btn.addEventListener("click", function () {
        img.src = btn.getAttribute("data-full");
        img.alt = btn.getAttribute("aria-label") || "";
        box.classList.add("open");
      });
    });
    box.addEventListener("click", function () { box.classList.remove("open"); img.src = ""; });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && box.classList.contains("open")) {
        box.classList.remove("open"); img.src = "";
      }
    });
  }
})();
