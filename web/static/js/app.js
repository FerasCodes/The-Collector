(() => {
  const state = {
    platform: "windows",
    favoritesOnly: false,
    category: "All",
    shell: "all",
    search: "",
    builder: [],
    selectedId: null,
    catalog: {},
  };

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  async function api(path, opts = {}) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || res.statusText);
    }
    return res.json();
  }

  function setStatus(msg) {
    $("#status").textContent = msg;
  }

  async function loadStats() {
    const s = await api("/api/stats");
    const text = `${s.total} commands available (${s.windows} Windows, ${s.linux} Linux)`;
    $("#repo-stats").textContent = text;
    $("#sidebar-stats").innerHTML = `${s.total} commands<br>${s.windows} Windows<br>${s.linux} Linux`;
  }

  async function loadCategories() {
    const cats = await api("/api/categories");
    const sel = $("#category");
    sel.innerHTML = '<option value="All">All topics</option>';
    cats.forEach((c) => {
      const o = document.createElement("option");
      o.value = c;
      o.textContent = c;
      sel.appendChild(o);
    });
  }

  async function loadProfiles() {
    const items = await api(`/api/profiles?platform=${state.platform}`);
    const sel = $("#profile-select");
    sel.innerHTML = "";
    items.forEach((p) => {
      const o = document.createElement("option");
      o.value = p.id;
      o.textContent = p.name;
      o.title = p.description;
      sel.appendChild(o);
    });
  }

  async function loadCommands() {
    const params = new URLSearchParams({
      platform: state.platform,
      search: state.search,
      shell: state.shell === "all" ? "" : state.shell,
      category: state.category === "All" ? "" : state.category,
      favorites: state.favoritesOnly ? "1" : "0",
    });
    const cmds = await api(`/api/commands?${params}`);
    cmds.forEach((c) => (state.catalog[c.id] = c));
    const tbody = $("#cmd-table tbody");
    tbody.innerHTML = "";
    cmds.forEach((c) => {
      const tr = document.createElement("tr");
      if (c.id === state.selectedId) tr.classList.add("selected");
      tr.innerHTML = `
        <td><button type="button" class="fav-btn" data-fav="${c.id}" title="Favorite">${c.favorite ? "★" : "☆"}</button></td>
        <td>${escapeHtml(c.name)}</td>
        <td>${escapeHtml(c.description)}</td>
        <td><button type="button" class="add-btn" data-add="${c.id}">Add</button></td>
      `;
      tr.addEventListener("click", (e) => {
        if (e.target.closest("button")) return;
        selectCommand(c.id);
      });
      tbody.appendChild(tr);
    });
    $("#list-count").textContent = `${cmds.length} shown`;
    setStatus(`Showing ${cmds.length} commands`);
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s || "";
    return d.innerHTML;
  }

  function selectCommand(id) {
    state.selectedId = id;
    $$("#cmd-table tbody tr").forEach((tr) => tr.classList.remove("selected"));
    const c = state.catalog[id];
    if (!c) return;
    const detail = [
      c.name,
      "=".repeat(c.name.length),
      "",
      `Description: ${c.description}`,
      "",
      `Syntax: ${c.syntax || "(see lines below)"}`,
      "",
      `Shell: ${c.shell}  |  Output: ${c.output_type}`,
      `OS: ${c.os_min || "any"} – ${c.os_max || "any"}`,
      `Platform: ${c.platform}`,
    ].join("\n");
    $("#detail").textContent = detail;
    loadCommands();
  }

  function renderBuilder() {
    const list = $("#builder-list");
    const n = state.builder.length;
    $("#builder-title").textContent = `Your script (${n} step${n !== 1 ? "s" : ""})`;
    if (!n) {
      list.innerHTML = `<div class="empty-builder">Your script is empty.<br><br>
        1. Pick a command and click <strong>Add</strong><br>
        2. Or use a <strong>Quick start</strong> profile on the left.</div>`;
      updatePreview();
      return;
    }
    list.innerHTML = "";
    state.builder.forEach((c) => {
      const card = document.createElement("div");
      card.className = "builder-card";
      card.innerHTML = `
        <h3>${escapeHtml(c.name)} <span class="muted">(${c.shell})</span></h3>
        <p class="meta">${escapeHtml(c.description)}</p>
        <div class="actions">
          <button type="button" class="btn small fav-toggle">${c.favorite ? "★ Favorited" : "☆ Save to favorites"}</button>
          <button type="button" class="remove">Remove</button>
        </div>
      `;
      card.querySelector(".remove").onclick = () => {
        state.builder = state.builder.filter((x) => x.id !== c.id);
        renderBuilder();
      };
      card.querySelector(".fav-toggle").onclick = async () => {
        const r = await api(`/api/favorites/${c.id}`, { method: "POST" });
        c.favorite = r.favorite;
        state.catalog[c.id] = c;
        renderBuilder();
        loadCommands();
      };
      list.appendChild(card);
    });
    updatePreview();
  }

  async function updatePreview() {
    if (!state.builder.length) {
      $("#preview").textContent = "Add commands to build your script.";
      $("#format-hint").textContent = "";
      return;
    }
    const format = document.querySelector('input[name="format"]:checked')?.value || "auto";
    const body = {
      command_ids: state.builder.map((c) => c.id),
      platform: state.platform,
      format,
      add_error_handling: $("#opt-errors").checked,
      add_header: $("#opt-header").checked,
      include_comments: $("#opt-comments").checked,
    };
    try {
      const r = await api("/api/build", { method: "POST", body: JSON.stringify(body) });
      let header = `# ${r.format_label} → ${r.path_hint}\n`;
      if (r.companion_path_hint) header += `# Also: ${r.companion_path_hint}\n`;
      header += "# ---\n\n";
      $("#preview").textContent = header + r.content;
      $("#format-hint").textContent = r.format_label;
      state.lastBuild = r;
    } catch (e) {
      $("#preview").textContent = `Error: ${e.message}`;
    }
  }

  function downloadScript() {
    if (!state.lastBuild) {
      alert("Add commands to your script first.");
      return;
    }
    downloadFile(state.lastBuild.path_hint, state.lastBuild.content);
    if (state.lastBuild.companion_content && state.lastBuild.companion_path_hint) {
      downloadFile(state.lastBuild.companion_path_hint, state.lastBuild.companion_content);
    }
    setStatus("Script downloaded");
  }

  function downloadFile(name, content) {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function addToBuilder(id) {
    const c = state.catalog[id];
    if (!c || state.builder.some((x) => x.id === id)) return;
    state.builder.push(c);
    renderBuilder();
    setStatus(`Added: ${c.name}`);
  }

  // Events
  $("#search").addEventListener("input", (e) => {
    state.search = e.target.value;
    loadCommands();
  });

  $$(".platform-toggle .plat").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".platform-toggle .plat").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.platform = btn.dataset.platform;
      if (state.platform === "linux") {
        document.querySelector('input[name="format"][value="sh"]').checked = true;
      } else {
        document.querySelector('input[name="format"][value="auto"]').checked = true;
      }
      loadProfiles();
      loadCommands();
    });
  });

  $("#btn-all").onclick = () => {
    state.favoritesOnly = false;
    loadCommands();
  };
  $("#btn-favorites").onclick = () => {
    state.favoritesOnly = true;
    loadCommands();
  };

  $("#category").onchange = (e) => {
    state.category = e.target.value;
    loadCommands();
  };

  $$('input[name="shell"]').forEach((r) => {
    r.onchange = () => {
      state.shell = r.value;
      loadCommands();
    };
  });

  $("#cmd-table").addEventListener("click", (e) => {
    const add = e.target.closest("[data-add]");
    if (add) {
      addToBuilder(add.dataset.add);
      return;
    }
    const fav = e.target.closest("[data-fav]");
    if (fav) {
      api(`/api/favorites/${fav.dataset.fav}`, { method: "POST" }).then((r) => {
        state.catalog[r.id] = { ...state.catalog[r.id], favorite: r.favorite };
        loadCommands();
      });
    }
  });

  $("#btn-profile").onclick = async () => {
    const id = $("#profile-select").value;
    if (!id) return;
    const cmds = await api(`/api/profiles/${id}/resolve`, { method: "POST" });
    state.builder = cmds;
    cmds.forEach((c) => (state.catalog[c.id] = c));
    renderBuilder();
    setStatus(`Loaded profile (${cmds.length} steps)`);
  };

  $("#btn-clear").onclick = $("#btn-clear-builder").onclick = () => {
    if (state.builder.length && !confirm("Clear all commands from your script?")) return;
    state.builder = [];
    renderBuilder();
  };

  $$('input[name="format"], #opt-errors, #opt-header, #opt-comments').forEach((el) => {
    el.addEventListener("change", updatePreview);
  });

  $("#btn-download").onclick = downloadScript;

  // Init
  (async () => {
    await loadStats();
    await loadCategories();
    await loadProfiles();
    await loadCommands();
    renderBuilder();
  })();
})();
