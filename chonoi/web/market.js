"use strict";
const byId = (id) => document.getElementById(id);
const guide = byId("guide"), cookbook = byId("cookbook");
const filters = [...cookbook.querySelectorAll("[data-filter]")];
let dishFilter = "all", lastBook = "", lastTools = "", lastMenu = "";
const modeNames = { gather: "Buổi sáng · Lặn hái", quan: "Buổi tối · Mở quán", day: "Chơi theo ngày" };

function toggleContrast() {
  highContrast = !highContrast;
  document.body.classList.toggle("contrast", highContrast);
  byId("contrast").setAttribute("aria-pressed", String(highContrast));
  cv.focus();
}
function openPanel(panel) {
  if (down.size) { down.clear(); pushInput(); }
  panel.showModal();
}
function openCookbook() {
  dishFilter = "all";
  lastBook = "";
  renderBook();
  openPanel(cookbook);
}
function handlePanelKey(e, k) {
  if (guide.open || cookbook.open) {
    if (cookbook.open && k === "c" && !e.repeat) { e.preventDefault(); cookbook.close(); }
    return true;
  }
  if (screen === "play") {
    return e.target instanceof HTMLButtonElement && (k === "enter" || k === " ");
  }
  if (e.repeat) return true;
  if (screen === "quit") {
    if (k === "enter" || k === "escape") { e.preventDefault(); screen = "menu"; }
    return true;
  }
  if (k === "escape") screen = "quit";
  else if (k === "arrowup" || k === "w") { e.preventDefault(); byId("start").focus(); }
  else if (k === "arrowdown" || k === "s") { e.preventDefault(); byId("exit").focus(); }
  else if (k === "c") openCookbook();
  else if ((k === "enter" || k === " ") && !(e.target instanceof HTMLButtonElement)) {
    e.preventDefault(); byId("start").click();
  }
  return true;
}

function element(tag, content, className) {
  const node = document.createElement(tag);
  if (content !== undefined) node.textContent = content;
  if (className) node.className = className;
  return node;
}
let lastSlip = "";
function statusCard(title, subtitle, lines, footer = "") {
  byId("status-layer").hidden = false;
  const key = JSON.stringify([title, subtitle, lines, footer]);
  if (key === lastSlip) return;
  lastSlip = key;
  const slip = document.querySelector(".slip");
  if (byId("slip-title").textContent !== title) slip.scrollTop = 0;
  byId("slip-title").textContent = title;
  byId("slip-sub").textContent = subtitle;
  byId("slip-lines").replaceChildren(...lines.map((line) => element("p", line)));
  byId("slip-foot").textContent = footer;
  byId("slip-foot").hidden = !footer;
}
function renderBook() {
  const menu = snap?.menu || {};
  const inShift = screen === "play" && ["gather", "quan"].includes(snap?.phase);
  const counts = inShift ? freshStockCounts() : {};
  const plan = snap?.day_plan?.dishes || {};
  const signature = JSON.stringify([menu, counts, plan, inShift, snap?.phase, dishFilter, offline]);
  if (signature === lastBook) return;
  lastBook = signature;
  byId("stock-source").textContent = inShift
    ? (snap.phase === "quan" ? "Đối chiếu với kho tươi sau khi trừ phần khách đã giữ." : "Đối chiếu với nguyên liệu tươi trong giỏ.")
    : "Công thức và giá bán của nhà bè.";
  for (const button of filters) {
    button.hidden = (button.dataset.filter === "ready" && !inShift) ||
      (button.dataset.filter === "plan" && (screen !== "play" || !Object.keys(plan).length));
    if (button.hidden && dishFilter === button.dataset.filter) dishFilter = "all";
  }
  filters.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.filter === dishFilter)));
  const list = byId("dish-list");
  list.replaceChildren();
  for (const [id, dish] of Object.entries(menu)) {
    const ingredients = Object.entries(dish.recipe);
    const ready = ingredients.every(([kind, n]) => (counts[kind] || 0) >= n);
    if ((dishFilter === "ready" && !ready) || (dishFilter === "plan" && !plan[id])) continue;
    const card = element("article", undefined, "dish"), header = element("header"), icon = element("canvas");
    icon.width = icon.height = 88;
    drawDishIcon(44, 44, 38, id, icon.getContext("2d"));
    header.append(icon, element("h3", dn(id)));
    card.append(header, element("p", `${dish.price}k · Nấu ${dish.cook_s} giây`));
    const portions = ingredients.map(([k, n]) => inShift ? `${KIND_NAME[k] || k} ${counts[k] || 0}/${n}` : `${KIND_NAME[k] || k} ×${n}`);
    card.append(element("p", portions.join(" · ")));
    if (inShift) card.append(element("p", ready ? "✓ Đủ nguyên liệu" : "Thiếu nguyên liệu", ready ? "availability ready" : "availability"));
    if (screen === "play" && plan[id]) card.append(element("p", `Trong ngày · ${plan[id]} phần`));
    list.append(card);
  }
  if (!list.children.length) list.append(element("p", Object.keys(menu).length
    ? "Chưa có món phù hợp với bộ lọc này." : offline ? "Mất kết nối tới máy chủ." : "Đang tải thực đơn…"));
}

function syncInterface() {
  const playing = screen === "play", shop = snap?.phase === "shop", finished = !!snap?.finished;
  const menuKey = [screen, snap?.mode, offline, restarting].join("|");
  if (lastMenu !== menuKey) {
    lastMenu = menuKey;
    byId("landing").hidden = playing;
    byId("game").hidden = !playing;
    document.querySelector(".welcome").hidden = screen === "quit";
    byId("farewell").hidden = screen !== "quit";
    byId("exit").hidden = screen === "quit";
    byId("start").disabled = restarting || offline || !snap;
    byId("session-mode").textContent = offline ? "Mất kết nối tới máy chủ" : modeNames[snap?.mode] || "Đang nối máy chủ…";
    if (playing) cv.focus();
    if (!snap || !playing) byId("status-layer").hidden = true;
  }
  const stopped = paused(), introducing = !!intro;
  const toolsKey = [screen, snap?.phase, finished, stopped, introducing].join("|");
  if (lastTools !== toolsKey) {
    lastTools = toolsKey;
    const shopping = shop && !finished && !stopped && !introducing;
    for (const id of ["shop-oxygen", "shop-hp", "shop-next"]) byId(id).hidden = !shopping;
    byId("pause").hidden = finished || introducing;
    byId("pause").firstChild.textContent = stopped ? "Tiếp tục " : "Tạm dừng ";
    byId("again").hidden = !finished;
    byId("home").hidden = !(finished || (stopped && !introducing));
    byId("touch-pad").hidden = !playing || shop || finished || stopped || introducing;
    byId("catch-button").hidden = snap?.phase !== "gather";
    if (byId("touch-pad").hidden && down.size && !down.has("pause")) { down.clear(); pushInput(); }
  }
  if (cookbook.open) renderBook();
}

byId("start").onclick = restart;
byId("again").onclick = restart;
byId("exit").onclick = () => { screen = "quit"; };
byId("return").onclick = byId("home").onclick = () => { screen = "menu"; };
byId("help").onclick = byId("guide-game").onclick = () => openPanel(guide);
byId("browse").onclick = byId("recipes").onclick = openCookbook;
byId("contrast").onclick = toggleContrast;
byId("pause").onclick = () => { tap("pause"); cv.focus(); };
byId("shop-next").onclick = () => { tap("shop_done"); cv.focus(); };
for (const id of ["oxygen", "hp"]) byId("shop-" + id).onclick = () => { oneShot.buy = id; pushInput(); cv.focus(); };
for (const panel of [guide, cookbook]) {
  panel.querySelector(".close").onclick = () => panel.close();
  panel.addEventListener("close", () => { if (screen === "play") cv.focus(); });
}
for (const button of filters) button.onclick = () => { dishFilter = button.dataset.filter; renderBook(); };
for (const button of document.querySelectorAll("[data-hold]")) {
  button.onpointerdown = (e) => {
    e.preventDefault();
    button.setPointerCapture(e.pointerId);
    down.add(button.dataset.hold);
    pushInput();
  };
  button.onlostpointercapture = () => { down.delete(button.dataset.hold); pushInput(); };
}
requestAnimationFrame(frame);
