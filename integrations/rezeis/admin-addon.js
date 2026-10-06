/*
 * Runtime-only Rezeis admin addon.
 *
 * Copy this file into the running Rezeis container and inject it from the
 * already-served SPA shell. It does not modify the Rezeis source repository.
 *
 * The addon intentionally uses Rezeis' existing authenticated /admin APIs:
 * the browser's current Bearer token is forwarded to the merge service, and
 * the merge service validates it against Rezeis before reading configUrl.
 */
(() => {
  "use strict";

  const MERGE_BASE = window.__REMNAWAVE_MERGE_URL__ || "";
  const path = () => window.location.pathname;

  if (!MERGE_BASE || window.__REZEIS_MERGE_ADDON_LOADED__) return;
  window.__REZEIS_MERGE_ADDON_LOADED__ = true;

  function token() {
    try {
      const value = localStorage.getItem("rezeis_admin_token");
      if (value) return value
    } catch (_) {}
    return "";
  }

  async function api(url, options = {}) {
    const headers = new Headers(options.headers || {});
    const t = token();
    if (t) headers.set("Authorization", "Bearer " + t);
    headers.set("Content-Type", "application/json");
    const response = await fetch(MERGE_BASE + url, {...options, headers});
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  function mountNav() {
    const nav = document.querySelector("nav");
    if (!nav || nav.querySelector("[data-remnawave-merge-nav]")) return;
    const item = document.createElement("a");
    item.href = "/subscription-merge";
    item.textContent = "Слияние подписок";
    item.dataset.remnawaveMergeNav = "1";
    item.style.cssText = "display:block;padding:8px 12px;cursor:pointer;";
    item.addEventListener("click", (event) => {
      event.preventDefault();
      history.pushState({}, "", "/subscription-merge");
      render();
    });
    nav.appendChild(item);
  }

  async function render() {
    if (path() !== "/subscription-merge") return;
    const root = document.querySelector("main") || document.querySelector("#root");
    if (!root) return;
    root.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.style.cssText = "padding:24px;max-width:1200px;margin:auto;";
    wrap.innerHTML = "<h1>Слияние подписок</h1><p>Загружаю подписки…</p>";
    root.appendChild(wrap);

    try {
      const page = await fetch("/api/admin/subscriptions?limit=100&page=1", {
        headers: {Authorization: "Bearer " + token()}
      }).then(r => r.json());
      const items = Array.isArray(page.items) ? page.items : [];
      wrap.innerHTML = "<h1>Слияние подписок</h1>";
      const form = document.createElement("div");
      form.style.cssText = "display:grid;grid-template-columns:1fr 1fr;gap:16px;";
      const selectMain = document.createElement("select");
      const selectSecondary = document.createElement("select");
      for (const [select, role] of [[selectMain,"Основная"],[selectSecondary,"Подключаемая"]]) {
        select.innerHTML = "<option value=''>Выберите " + role.toLowerCase() + " подписку</option>";
        for (const sub of items) {
          if (!sub.userTelegramId) continue;
          const option = document.createElement("option");
          option.value = JSON.stringify({subscriptionId: sub.id, userTelegramId: String(sub.userTelegramId)});
          option.textContent = [sub.plan?.name || "Без тарифа", sub.user?.name || "Без имени", sub.userTelegramId, sub.status].join(" · ");
          select.appendChild(option);
        }
      }
      form.append(selectMain, selectSecondary);
      const button = document.createElement("button");
      button.textContent = "Создать объединённую подписку";
      button.style.cssText = "margin-top:16px;padding:10px 16px;cursor:pointer;";
      const result = document.createElement("pre");
      result.style.cssText = "margin-top:16px;white-space:pre-wrap;";
      button.onclick = async () => {
        if (!selectMain.value || !selectSecondary.value) return;
        const main = JSON.parse(selectMain.value), secondary = JSON.parse(selectSecondary.value);
        if (main.subscriptionId === secondary.subscriptionId) {
          result.textContent = "Основная и подключаемая подписки должны быть разными.";
          return;
        }
        try {
          const created = await api("/api/admin/merge/pairs", {
            method: "POST",
            body: JSON.stringify({main, secondary})
          });
          result.textContent = "Готово. Клиентская ссылка:\n" + new URL(created.subscriptionUrl, MERGE_BASE).href;
        } catch (error) {
          result.textContent = "Ошибка: " + error.message;
        }
      };
      wrap.append(form, button, result);
    } catch (error) {
      wrap.lastChild.textContent = "Ошибка загрузки подписок: " + error.message;
    }
  }

  window.addEventListener("popstate", render);
  new MutationObserver(() => { mountNav(); render(); }).observe(document.documentElement, {childList:true,subtree:true});
  mountNav();
  render();
})();
